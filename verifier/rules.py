"""Straight drops on a board packed into ten-bit rows, bottom row in the low bits."""

from contract import LegalPlacementsOutput, MoveOutput, Placement, TurnInput

WIDTH = 10
HEIGHT = 8
FULL = (1 << WIDTH) - 1
TOP_OUT = WIDTH * HEIGHT + 1
SHAPES = {
    "I": ("####",),
    "J": ("#..", "###"),
    "L": ("..#", "###"),
    "O": ("##", "##"),
    "S": (".##", "##."),
    "T": (".#.", "###"),
    "Z": ("##.", ".##"),
}


def pack(rows):
    return sum(
        1 << ((HEIGHT - 1 - y) * WIDTH + x) for y, row in enumerate(rows) for x, cell in enumerate(row) if cell == "#"
    )


def unpack(board):
    return [
        "".join("#" if board & (1 << (y * WIDTH + x)) else "." for x in range(WIDTH)) for y in reversed(range(HEIGHT))
    ]


def turn_error(turn):
    if not isinstance(turn, TurnInput) or not isinstance(turn.board, list) or len(turn.board) != HEIGHT:
        return "Expected eight board rows."
    if any(not isinstance(row, str) or len(row) != WIDTH or set(row) - {".", "#"} for row in turn.board):
        return "Each board row must contain ten cells using . and #."
    if "#" * WIDTH in turn.board:
        return "The board contains an uncleared full row."
    if not isinstance(turn.current, str) or turn.current not in SHAPES:
        return "Unknown current piece."
    if (
        not isinstance(turn.remaining, list)
        or len(turn.remaining) > 3
        or any(not isinstance(piece, str) or piece not in SHAPES for piece in turn.remaining)
    ):
        return "Expected at most three hidden tetrominoes."
    if len({turn.current, *turn.remaining}) != 1 + len(turn.remaining):
        return "A seven-piece bag cannot contain duplicates."
    return None


def rotations(rows):
    for _ in range(4):
        yield rows
        rows = tuple("".join(column) for column in zip(*reversed(rows)))


MASKS = {
    piece: tuple(
        tuple(
            (
                pack(["." * WIDTH] * (HEIGHT - len(rows)) + [row.ljust(WIDTH, ".") for row in rows]) << x,
                HEIGHT - len(rows),
            )
            for x in range(WIDTH + 1 - len(rows[0]))
        )
        for rows in rotations(shape)
    )
    for piece, shape in SHAPES.items()
}


def moves(piece):
    for orientation, columns in enumerate(MASKS[piece]):
        for column in range(len(columns)):
            yield orientation, column


def legal(piece, move):
    return (
        isinstance(move, MoveOutput)
        and type(move.orientation) is int
        and type(move.column) is int
        and 0 <= move.orientation < 4
        and 0 <= move.column < len(MASKS[piece][move.orientation])
    )


def landing(board, piece, orientation, column):
    mask, lift = MASKS[piece][orientation][column]
    falling = mask << (lift * WIDTH)
    if board & falling:
        return None
    while lift and not board & (falling >> WIDTH):
        falling >>= WIDTH
        lift -= 1
    return falling


def drop(board, piece, orientation, column):
    falling = landing(board, piece, orientation, column)
    if falling is None:
        return None, 0
    locked = board | falling
    compact = 0
    kept = 0
    for y in range(HEIGHT):
        row = (locked >> (y * WIDTH)) & FULL
        if row != FULL:
            compact |= row << (kept * WIDTH)
            kept += 1
    return compact, HEIGHT - kept


def placements(turn):
    board = pack(turn.board)
    result = []
    for orientation, column in moves(turn.current):
        after, cleared = drop(board, turn.current, orientation, column)
        result.append(
            Placement(
                MoveOutput(orientation, column), unpack(board if after is None else after), cleared, after is None
            )
        )
    return LegalPlacementsOutput(result)
