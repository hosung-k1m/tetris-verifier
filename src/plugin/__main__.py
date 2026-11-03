import json
import os
from pathlib import Path

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, Tool
from verifier import COMMIT_LOG, verify_input
from verifier.puzzles import prefix
from verifier.rules import placements

server = Server("tetris-verifier")
committed = None


@server.list_tools()
async def list_tools():
    return [
        types.Tool(name=tool.value, inputSchema=output_schema(given), outputSchema=output_schema(made))
        for tool, (given, made) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name, arguments):
    global committed
    tool = Tool(name)
    given, _ = TOOLS[tool]
    value = build_output(arguments, given)
    verdict = verify_input(tool, value)
    if not verdict["valid"]:
        raise ValueError(verdict["message"])
    match tool:
        case Tool.LEGAL:
            output = placements(value)
        case Tool.PLAY:
            log = Path(os.environ["NANOAGENT_WORKSPACE"]) / COMMIT_LOG
            submission = plain_output(value)
            if committed is not None:
                prior = committed
                if (
                    submission["puzzle"] != prior["puzzle"]
                    or len(value.moves) != len(prior["moves"]) + 1
                    or submission["moves"][:-1] != prior["moves"]
                ):
                    raise ValueError("Append exactly one move to the committed prefix.")
            elif value.moves:
                raise ValueError("Open the puzzle with an empty prefix.")
            output = prefix(value.puzzle, value.moves)
            temporary = log.with_suffix(".tmp")
            temporary.write_text(json.dumps(submission), encoding="utf-8")
            temporary.replace(log)
            committed = submission
    return plain_output(output)


async def run():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(run)
