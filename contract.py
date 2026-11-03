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
class Rotation(Output):
    shape: Annotated[list[str], "Occupied cells marked #, top row first"]
    columns: Annotated[list[int], "Zero-based columns where the piece can enter the board"]
    clears: Annotated[list[int], "Immediate row clears for each listed column"]


@dataclass
class PrefixOutput(Output):
    turn: TurnInput | None
    rotations: Annotated[list[Rotation], "Shapes and columns indexed by clockwise quarter turns"]


TOOLS = {
    Tool.LEGAL: (LegalPlacementsInput, LegalPlacementsOutput),
    Tool.PLAY: (PrefixInput, PrefixOutput),
}
TASKS = {
    Task.CHOOSE: (TurnInput, MoveOutput),
    Task.PLAY: (PuzzleInput, GameOutput),
}
