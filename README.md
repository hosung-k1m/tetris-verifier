# Tetris: No Peek

Ask the AI to play a puzzle, then open Result to see every drop and its optimality verdict.

prompt - "play the game"

The default puzzle is `stack`. Ask for `split` to watch the shorter puzzle.

The board is 10 columns by 8 rows. Orientations count clockwise turns from the shapes in `verifier/rules.py`, and columns are zero-based bounding-box positions. A straight drop that cannot enter the board ends the puzzle with a top-out score of 81. Otherwise the score counts cells after the final lock and row clears. Each move is checked from the actual board and visible bag at that turn, against every possible reveal. Every tied optimum passes.

## Tools

`play-puzzle` uses `play_prefix` to open a curated fixture and commit one placement at a time. The next piece is revealed only after the tool records the commitment. The AI submits its final drop directly because there is no next piece to reveal. The verifier checks the earlier moves against the tool-owned record and independently replays and grades every drop. The entire puzzle passes if it is complete and every move was optimal.

`choose-optimal-move` grades a single placement on a custom turn. Its `legal_placements` tool reports the immediate consequences of a drop.

## Layout

The contract is in `contract.py`, the verifier and puzzles in `verifier/`, the MCP server in `src/plugin/`, and the Result tab renderers in `ui/`.

## Develop and run

Run `uv sync --frozen --extra dev` and `uv run --frozen --extra dev pytest` from the plugin root. Use `nanoagent plugin inspect .` to validate the manifest and page assets.
