from contract import PrefixOutput, RotationPreview, TurnInput

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


def prefix(name, committed):
    turn, _ = replay(name, committed)
    if turn is None:
        return PrefixOutput(None, [])
    board = pack(turn.board)
    previews = []
    for orientation, shape in enumerate(rotations(SHAPES[turn.current])):
        drops = []
        for column in range(WIDTH - len(shape[0]) + 1):
            after, cleared = drop(board, turn.current, orientation, column)
            if after is None:
                drops.append([])
                continue
            heights = [len(stack.lstrip(".")) for stack in map("".join, zip(*unpack(after)))]
            drops.append([cleared, sum(heights) - after.bit_count(), max(heights)])
        previews.append(RotationPreview(list(shape), drops))
    return PrefixOutput(turn, previews)
