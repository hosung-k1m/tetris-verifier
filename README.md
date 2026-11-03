# Tetris: No Peek

Ask RUSH Lab to play a puzzle (`stack` or `split`). The AI plays every turn. Open Result to see each placement, its starting and resulting boards, and whether it was optimal.

The board is 10 columns by 8 rows. Orientations count clockwise turns from the shapes in `verifier/rules.py`, and columns are zero-based bounding-box positions. A straight drop that cannot enter the board ends the puzzle with a top-out score of 81. Otherwise the score counts cells after the final lock and row clears. Each move is checked from the actual board and visible bag at that turn, against every possible reveal. Every tied optimum passes.

## Tools

`play-puzzle` uses `play_prefix` to open a curated fixture and commit one placement at a time. The next piece is revealed only after the tool records the commitment. The verifier checks the submitted list against this tool-owned record and independently replays and grades each move. The entire puzzle passes if it is complete and every move was optimal.

`choose-optimal-move` grades a single placement on a custom turn. Its `legal_placements` tool reports the immediate consequences of a drop.

## Layout

The contract is in `contract.py`, the verifier and puzzles in `verifier/`, the MCP server in `src/plugin/`, and the Result tab renderers in `ui/`.

## Develop and run

Run `uv sync --frozen --extra dev` and `uv run --frozen --extra dev pytest` from the plugin root. Use `nanoagent plugin inspect .` to validate the manifest and page assets.
