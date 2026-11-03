import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, CompareOutput, Tool
from verifier import verify_input
from verifier.puzzles import puzzle
from verifier.rules import placements

server = Server("tetris-verifier")


@server.list_tools()
async def list_tools():
    return [
        types.Tool(name=tool.value, inputSchema=output_schema(given), outputSchema=output_schema(made))
        for tool, (given, made) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name, arguments):
    tool = Tool(name)
    given, _ = TOOLS[tool]
    value = build_output(arguments, given)
    verdict = verify_input(tool, value)
    if not verdict["valid"]:
        raise ValueError(verdict["message"])
    match tool:
        case Tool.LEGAL:
            output = placements(value)
        case Tool.START:
            output = puzzle(value.puzzle)
        case Tool.COMPARE:
            output = CompareOutput(value.turn, value.player, value.agent)
    return plain_output(output)


async def run():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(run)
