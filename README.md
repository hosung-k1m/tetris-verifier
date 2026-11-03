# Tetris: No Peek

Ask RUSH Lab to start a puzzle (`split` or `stack`). Open the Result tab, preview a drop, and commit it. The agent then plays the same turn. The comparison shows both verified outcomes, with a worst-order replay for each legal suboptimal move.

The board is 10 columns by 8 rows. Orientations count clockwise turns from the shapes in `verifier/rules.py`, and columns are zero-based bounding-box positions. A straight drop that cannot enter the board ends the puzzle with a top-out score of 81. Otherwise the score counts cells after the final lock and row clears. The verifier minimizes the worst score over possible reveals, choosing a new best response after each reveal. Every tied optimum passes.

## Tools


`legal_placements` reports only the immediate consequences of a drop. The `choose-optimal-move` agent task recomputes the exact optimum and grades the submitted placement. The comparison applies the same evaluator to both moves. Neither verifier needs network access or workspace files.

`start-puzzle` uses `start_puzzle` to load the selected local fixture. After the agent submits, `compare-moves` uses `compare_moves` to carry both committed placements into the comparison verifier.


## Layout

The contract is in `contract.py`, the verifier and puzzles in `verifier/`, the MCP server in `src/plugin/`, and the Result tab renderers in `ui/`.

## Develop and run


Run `uv sync --frozen --extra dev` and `uv run --frozen --extra dev pytest` from the plugin root. Use `nanoagent plugin inspect .` to validate the manifest and page assets.
