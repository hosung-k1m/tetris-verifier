import json
from pathlib import Path

from contract import Task, Tool

from .puzzles import PUZZLES, prefix, replay
from .rules import landing, legal, pack, placements, turn_error, unpack
from .search import grade

COMMIT_LOG = "tetris-committed.json"


def result(valid, message, **details):
    return {"valid": valid, "score": int(valid), "message": message, "details": details}


def verify_input(tool, value):
    if Tool(tool) is Tool.LEGAL:
        error = turn_error(value)
        return result(error is None, error or "Input is valid.")
    if value.puzzle not in PUZZLES:
        return result(False, "Unknown puzzle.")
    try:
        replay(value.puzzle, value.moves)
    except ValueError as error:
        return result(False, str(error))
    return result(True, "Input is valid.")


def verify_output(tool, input_value, output_value, workspace):
    checked = verify_input(tool, input_value)
    if not checked["valid"]:
        return checked
    expected = placements(input_value) if Tool(tool) is Tool.LEGAL else prefix(input_value.puzzle, input_value.moves)
    if output_value != expected:
        return result(False, "Tool output does not match the rules.")
    return result(True, "Tool output verified.")


def verify_move(turn, move):
    error = turn_error(turn)
    if error:
        return result(False, error, status="malformed_turn")
    if not legal(turn.current, move):
        return result(False, "Illegal orientation or column.", status="illegal_move")
    [graded] = grade(turn, move)
    optimal = graded["status"] == "optimal"
    return result(optimal, "Optimal placement." if optimal else "A better placement exists.", **graded)


def verify_task(task, arguments, output, reference, workspace):
    if Task(task) is Task.CHOOSE:
        return verify_move(arguments, output)

    if arguments.puzzle not in PUZZLES:
        return result(False, "Unknown puzzle.", moves=[])
    log = Path(workspace) / COMMIT_LOG
    if not log.is_file():
        return result(False, "No placements were committed through the play tool.", moves=[])
    committed = json.loads(log.read_text(encoding="utf-8"))
    submitted = [{"orientation": move.orientation, "column": move.column} for move in output.moves]
    committed_count = len(committed["moves"])
    if committed != {"puzzle": arguments.puzzle, "moves": submitted[:committed_count]}:
        return result(False, "Submission differs from the committed placements.", moves=[])
    if len(submitted) > committed_count:
        final_turn, _ = replay(arguments.puzzle, output.moves[:committed_count])
        if len(submitted) != committed_count + 1 or final_turn is None or final_turn.remaining:
            return result(False, "Only the last drop can be submitted without a play tool call.", moves=[])
        if not legal(final_turn.current, output.moves[-1]):
            return result(False, "Illegal orientation or column on the last drop.", moves=[])

    turn, steps = replay(arguments.puzzle, output.moves)
    graded = []
    for before, move, board, cleared, top_out in steps:
        check = verify_move(before, move)["details"]
        optimal_move = check.get("optimal_move", move)
        graded.append(
            {
                "turn": before,
                "move": move,
                "board": board,
                "cleared": cleared,
                "top_out": top_out,
                "placed_cells": drop_cells(before, move),
                "optimal_cells": drop_cells(before, optimal_move),
                **check,
            }
        )
    if turn is not None:
        return result(False, "The puzzle ended before all required pieces were placed.", moves=graded)
    optimal = all(move["status"] == "optimal" for move in graded)
    return result(
        optimal, "Every placement was optimal." if optimal else "Some placements were suboptimal.", moves=graded
    )


def drop_cells(turn, move):
    """Mark the four landing cells before any row clears."""
    cells = landing(pack(turn.board), turn.current, move.orientation, move.column)
    return None if cells is None else unpack(cells)
