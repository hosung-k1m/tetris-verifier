from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    LEGAL = "legal_placements"
    START = "start_puzzle"
    COMPARE = "compare_moves"


class Task(Enum):
    CHOOSE = "choose-optimal-move"
    START = "start-puzzle"
    COMPARE = "compare-moves"


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
class PuzzleOutput(Output):
    turn: TurnInput
    placements: list[Placement]


@dataclass
class CompareInput(Output):
    turn: TurnInput
    player: MoveOutput
    agent: MoveOutput


@dataclass
class CompareOutput(CompareInput):
    pass


TOOLS = {
    Tool.LEGAL: (LegalPlacementsInput, LegalPlacementsOutput),
    Tool.START: (PuzzleInput, PuzzleOutput),
    Tool.COMPARE: (CompareInput, CompareOutput),
}
TASKS = {
    Task.CHOOSE: (TurnInput, MoveOutput),
    Task.START: TOOLS[Tool.START],
    Task.COMPARE: TOOLS[Tool.COMPARE],
}
