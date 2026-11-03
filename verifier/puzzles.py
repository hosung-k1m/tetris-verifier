from contract import PuzzleOutput, TurnInput

from .rules import placements

PUZZLES = {
    "split": ([".........."] * 6 + ["###...####", "####.#####"], "T", []),
    "stack": ([".........."] * 6 + ["..##......", "##..###..#"], "L", ["I", "O", "T"]),
}


def puzzle(name):
    rows, current, remaining = PUZZLES[name]
    turn = TurnInput(list(rows), current, list(remaining))
    return PuzzleOutput(turn, placements(turn).placements)
