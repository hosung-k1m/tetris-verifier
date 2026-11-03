from contract import PrefixOutput, TurnInput

from .rules import drop, legal, pack, placements, unpack

PUZZLES = {
    "split": ([".........."] * 6 + ["###...####", "####.#####"], "T", ()),
    "stack": ([".........."] * 6 + ["..##......", "##..###..#"], "L", ("O", "T", "I")),
}


def puzzle(name):
    rows, current, order = PUZZLES[name]
    return TurnInput(list(rows), current, sorted(order))


def replay(name, moves):
    turn = puzzle(name)
    _, _, order = PUZZLES[name]
    steps = []
    for index, move in enumerate(moves):
        if turn is None:
            raise ValueError("A move was submitted after the puzzle ended.")
        if not legal(turn.current, move):
            raise ValueError("Illegal orientation or column.")
        after, cleared = drop(pack(turn.board), turn.current, move.orientation, move.column)
        board = turn.board if after is None else unpack(after)
        steps.append((turn, move, board, cleared, after is None))
        turn = (
            TurnInput(board, order[index], sorted(order[index + 1 :]))
            if after is not None and index < len(order)
            else None
        )
    return turn, steps


def prefix(name, moves):
    turn, _ = replay(name, moves)
    return PrefixOutput(turn, [] if turn is None else placements(turn).placements)
