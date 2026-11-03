from functools import cache
from itertools import pairwise, permutations

import pytest

from contract import LegalPlacementsInput, MoveOutput, Task, Tool, TurnInput
from verifier import verify_input, verify_output, verify_task
from verifier.puzzles import puzzle
from verifier.rules import TOP_OUT, drop, moves, pack, placements, unpack

EMPTY = [".........."] * 8


def verdict(turn, orientation, column):
    return verify_task(Task.CHOOSE, turn, MoveOutput(orientation, column), None, None)


def test_unique_optimum():
    turn = puzzle("split")
    results = [((rotation, col), verdict(turn, rotation, col)) for rotation, col in moves(turn.current)]
    assert [move for move, result in results if result["valid"]] == [(2, 3)]
    assert verdict(turn, 2, 3)["details"]["submitted_score"] == 0
    assert verdict(turn, 0, 3)["details"]["submitted_score"] == 10


def test_tied_nonzero_optima():
    turn = TurnInput(EMPTY, "I", [])
    for rotation, col in ((0, 0), (1, 9), (3, 3)):
        result = verdict(turn, rotation, col)
        assert result["valid"] and result["score"] == 1
        assert result["details"]["submitted_score"] == result["details"]["optimal_score"] == 4


def test_foreknowledge_does_not_count_and_worst_branch_replays():
    turn = puzzle("stack")
    submitted = (0, 3)
    initial, _ = drop(pack(turn.board), turn.current, *submitted)

    @cache
    def known_order(board, order):
        if not order:
            return board.bit_count()
        piece, *tail = order
        return min(
            TOP_OUT if (after := drop(board, piece, *move)[0]) is None else known_order(after, tuple(tail))
            for move in moves(piece)
        )

    # A solver that plans for a favorable reveal order can match the optimum.
    # A move must withstand every order to pass the actual verifier.
    assert {known_order(initial, order) for order in permutations(turn.remaining)} == {14, 24}
    result = verdict(turn, *submitted)
    assert (result["valid"], result["score"]) == (False, 0)
    details = result["details"]
    assert (details["submitted_score"], details["optimal_score"]) == (24, 14)
    board = pack(turn.board)
    replay = details["replay"]
    assert replay[0]["move"] == MoveOutput(*submitted)
    assert replay[0]["piece"] == turn.current
    assert sorted(step["piece"] for step in replay[1:]) == sorted(turn.remaining)
    for step in replay:
        board, cleared = drop(board, step["piece"], step["move"].orientation, step["move"].column)
        assert not step["top_out"]
        assert (unpack(board), cleared) == (step["board"], step["cleared"])
    assert board.bit_count() == details["submitted_score"]
    shuffled = TurnInput(turn.board, turn.current, list(reversed(turn.remaining)))
    assert verdict(shuffled, *submitted) == result


def test_top_out_is_legal_but_worse_than_surviving():
    turn = TurnInput(["#........."] + EMPTY[1:], "I", [])
    result = verdict(turn, 0, 0)
    details = result["details"]
    assert (details["status"], details["submitted_score"], details["optimal_score"]) == ("suboptimal", 81, 5)
    [step] = details["replay"]
    assert step["top_out"] and step["board"] == turn.board and step["cleared"] == 0


@pytest.mark.parametrize("orientation,column", [(-1, 0), (4, 0), (0, 7), (1, -1)])
def test_illegal_move(orientation, column):
    result = verdict(TurnInput(EMPTY, "I", []), orientation, column)
    assert not result["valid"] and result["details"]["status"] == "illegal_move"


@pytest.mark.parametrize(
    "turn",
    [
        TurnInput(EMPTY[1:], "I", []),
        TurnInput(["##########"] + EMPTY[1:], "I", []),
        TurnInput(EMPTY, "A", []),
        TurnInput(EMPTY, "I", ["I"]),
        TurnInput(EMPTY, "I", ["T", "O", "T"]),
        TurnInput(EMPTY, "I", ["T", "O", "S", "Z"]),
    ],
)
def test_malformed_turn(turn):
    assert not verify_input(Tool.LEGAL, turn)["valid"]
    assert verdict(turn, 0, 0)["details"]["status"] == "malformed_turn"


def test_tool_checks_immediate_boards_and_all_placements():
    from contract import LegalPlacementsOutput

    opening = puzzle("split")
    turn = opening
    tool_input = LegalPlacementsInput(turn.board, turn.current, turn.remaining)
    output = placements(turn)
    perfect = next(p for p in output.placements if p.move == MoveOutput(2, 3))
    assert (perfect.board, perfect.cleared, perfect.top_out) == (EMPTY, 2, False)
    assert verify_output(Tool.LEGAL, tool_input, output, None)["valid"]
    perfect.cleared = 1
    assert not verify_output(Tool.LEGAL, tool_input, output, None)["valid"]
    assert not verify_output(Tool.LEGAL, tool_input, LegalPlacementsOutput([]), None)["valid"]


def test_game_grades_each_committed_turn_and_rejects_rewritten_history(tmp_path):
    import json

    from contract import GameOutput, PuzzleInput
    from verifier import COMMIT_LOG
    from verifier.puzzles import replay
    from verifier.search import grade

    name = "stack"
    played = [MoveOutput(0, 3)]
    turn, _ = replay(name, played)
    while turn is not None:
        candidates = [placement.move for placement in placements(turn).placements]
        grades = grade(turn, *candidates)
        played.append(
            next(move for move, check in zip(candidates, grades, strict=True) if check["status"] == "optimal")
        )
        turn, _ = replay(name, played)

    log = tmp_path / COMMIT_LOG
    log.write_text(
        json.dumps(
            {"puzzle": name, "moves": [{"orientation": move.orientation, "column": move.column} for move in played]}
        )
    )
    result = verify_task(Task.PLAY, PuzzleInput(name), GameOutput(played), None, tmp_path)
    assert not result["valid"]
    steps = result["details"]["moves"]
    assert [step["turn"].current for step in steps] == ["L", "O", "T", "I"]
    assert [step["status"] for step in steps] == ["suboptimal", "optimal", "optimal", "optimal"]
    assert all(after["turn"].board == before["board"] for before, after in pairwise(steps))

    changed = verify_task(Task.PLAY, PuzzleInput(name), GameOutput(played[1:]), None, tmp_path)
    assert not changed["valid"]
    assert "differs" in changed["message"]
