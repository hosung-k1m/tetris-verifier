from contract import PrefixOutput, Rotation, TurnInput

from .rules import SHAPES, WIDTH, drop, legal, pack, rotations, unpack

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
    if turn is None:
        return PrefixOutput(None, [])
    board = pack(turn.board)
    options = []
    for orientation, shape in enumerate(rotations(SHAPES[turn.current])):
        columns, clears = [], []
        for column in range(WIDTH - len(shape[0]) + 1):
            after, cleared = drop(board, turn.current, orientation, column)
            if after is not None:
                columns.append(column)
                clears.append(cleared)
        options.append(Rotation(list(shape), columns, clears))
    return PrefixOutput(turn, options)
