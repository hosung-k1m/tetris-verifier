from contract import CompareOutput, Task, Tool

from .puzzles import PUZZLES, puzzle
from .rules import legal, placements, turn_error
from .search import grade


def result(valid, message, **details):
    return {"valid": valid, "score": int(valid), "message": message, "details": details}


def verify_input(tool, value):
    match Tool(tool):
        case Tool.LEGAL:
            error = turn_error(value)
        case Tool.START:
            error = None if value.puzzle in PUZZLES else "Unknown puzzle."
        case Tool.COMPARE:
            error = turn_error(value.turn)
    return result(error is None, error or "Input is valid.")


def verify_output(tool, input_value, output_value, workspace):
    checked = verify_input(tool, input_value)
    if not checked["valid"]:
        return checked
    match Tool(tool):
        case Tool.LEGAL:
            expected = placements(input_value)
        case Tool.START:
            expected = puzzle(input_value.puzzle)
        case Tool.COMPARE:
            expected = CompareOutput(input_value.turn, input_value.player, input_value.agent)
    if output_value != expected:
        return result(False, "Tool output does not match the rules.")
    return result(True, "Tool output verified.")


def verify_task(task, arguments, output, reference, workspace):
    match Task(task):
        case Task.START:
            return verify_output(Tool.START, arguments, output, workspace)
        case Task.COMPARE:
            checked = verify_output(Tool.COMPARE, arguments, output, workspace)
            if not checked["valid"]:
                return checked
            player, agent = grade(arguments.turn, arguments.player, arguments.agent)
            return result(True, "Both placements evaluated.", player=player, agent=agent)
        case Task.CHOOSE:
            error = turn_error(arguments)
            if error:
                return result(False, error, status="malformed_turn")
            if not legal(arguments.current, output):
                return result(False, "Illegal orientation or column.", status="illegal_move")
            [graded] = grade(arguments, output)
            optimal = graded["status"] == "optimal"
            return result(optimal, "Optimal placement." if optimal else "A better placement exists.", **graded)
