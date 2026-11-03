from contract import Candidate, MoveOutput, PrefixOutput, TurnInput

from .rules import drop, legal, moves, pack, unpack

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


def prefix(name, committed):
    turn, _ = replay(name, committed)
    if turn is None:
        return PrefixOutput(None, [])
    board = pack(turn.board)
    options = []
    seen = set()
    for orientation, column in moves(turn.current):
        after, cleared = drop(board, turn.current, orientation, column)
        if after in seen:
            continue
        seen.add(after)
        resulting_board = board if after is None else after
        heights = [len(stack.lstrip(".")) for stack in map("".join, zip(*unpack(resulting_board)))]
        holes = sum(heights) - resulting_board.bit_count()
        options.append(Candidate(MoveOutput(orientation, column), cleared, holes, max(heights), after is None))
    options.sort(key=lambda option: (option.top_out, -option.cleared, option.holes, option.height))
    return PrefixOutput(turn, options[:4])
