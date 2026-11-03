from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    LEGAL = "legal_placements"
    PLAY = "play_prefix"


class Task(Enum):
    CHOOSE = "choose-optimal-move"
    PLAY = "play-puzzle"


@dataclass
class TurnInput(Output):
    board: Annotated[list[str], "Eight rows, top first, each ten characters: . empty, # occupied"]
    current: Annotated[str, "Visible piece: I, J, L, O, S, T or Z"]
    remaining: Annotated[list[str], "Unordered set of zero to three distinct hidden pieces"]


@dataclass
class MoveOutput(Output):
    orientation: Annotated[int, "Clockwise quarter turns from spawn, 0 through 3"]
    column: Annotated[int, "Zero-based left edge of the rotated bounding box"]


@dataclass
class Placement(Output):
    move: MoveOutput
    board: list[str]
    cleared: int
    top_out: bool


@dataclass
class LegalPlacementsInput(TurnInput):
    pass


@dataclass
class LegalPlacementsOutput(Output):
    placements: list[Placement]


@dataclass
class PuzzleInput(Output):
    puzzle: Annotated[str, "Curated puzzle: split or stack"]


@dataclass
class GameOutput(Output):
    moves: Annotated[list[MoveOutput], "Every committed placement in order"]


@dataclass
class PrefixInput(PuzzleInput):
    moves: Annotated[list[MoveOutput], "The committed prefix, empty to open, then append one move per call"]


@dataclass
class PlayTurn(TurnInput):
    board: Annotated[list[str], "Board with empty rows above the stack omitted"]


@dataclass
class PrefixOutput(Output):
    turn: PlayTurn | None
    drops: Annotated[
        list[list[int]],
        "Up to eight rows: [orientation, column, clears, holes, height], or [orientation, column] for top-out",
    ]


TOOLS = {
    Tool.LEGAL: (LegalPlacementsInput, LegalPlacementsOutput),
    Tool.PLAY: (PrefixInput, PrefixOutput),
}
TASKS = {
    Task.CHOOSE: (TurnInput, MoveOutput),
    Task.PLAY: (PuzzleInput, GameOutput),
}
