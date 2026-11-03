from contract import PlayTurn, PrefixOutput, TurnInput

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
        rows = unpack(resulting_board)
        heights = [len(stack.lstrip(".")) for stack in map("".join, zip(*rows))]
        holes = sum(heights) - resulting_board.bit_count()
        option = [orientation, column]
        if after is not None:
            option.extend((cleared, holes, max(heights)))
        options.append(((after is None, -cleared, holes, max(heights)), option))
    options.sort()
    shortlist = sorted(option for _, option in options[:8])
    first = next((index for index, row in enumerate(turn.board) if "#" in row), len(turn.board))
    return PrefixOutput(PlayTurn(turn.board[first:], turn.current, turn.remaining), shortlist)
