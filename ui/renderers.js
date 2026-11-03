import { h } from "./kit/components.js";

function grid(rows, label, overlay, color) {
  return h("div", { class: "tetris-grid", role: "img", "aria-label": label },
    rows.flatMap((row, y) => [...row].map((cell, x) => h("span", {
      class: overlay?.[y][x] === "#" ? color : cell === "#" ? "filled" : "empty",
    }))));
}

const moveLabel = move => `${90 * move.orientation}° clockwise · column ${move.column + 1}`;
const scoreLabel = score => score === 81 ? "Top-out (81)" : `${score} cells left`;

function outcome(graded) {
  return [
    h("p", { text: graded.status === "optimal" ? "Optimal placement" : "Suboptimal placement" }),
    h("p", { text: `Worst outcome: ${scoreLabel(graded.submitted_score)} · Best possible: ${scoreLabel(graded.optimal_score)}` }),
  ];
}

function dropPanel(title, color, turn, move, cells, score) {
  return h("section", {},
    h("h5", { class: color, text: title }),
    h("p", { text: moveLabel(move) }),
    grid(turn.board, `${title} on the board before row clears`, cells, color),
    cells === null ? h("p", { text: "Top-out · piece could not enter" }) : null,
    h("p", { text: `Worst case: ${scoreLabel(score)}` }),
  );
}

function game(_value, { verdict }) {
  const moves = verdict.details.moves;
  if (!moves.length) return h("p", { text: verdict.message });
  const optimal = moves.filter(step => step.status === "optimal").length;
  return h("section", {},
    h("p", { class: "tetris-summary", text: `${optimal} of ${moves.length} drops optimal` }),
    h("p", { text: "Worst case shows how many cells could remain after all pieces are played. Lower is better." }),
    h("ol", { class: "tetris-moves" }, moves.map((step, index) => {
      const matched = step.status === "optimal";
      return h("li", {},
        h("header", { class: "tetris-move-heading" },
          h("h4", { text: `Move ${index + 1} · ${step.turn.current} piece` }),
          h("span", { class: `tetris-badge ${matched ? "best-drop" : "ai-drop"}`,
            text: matched ? "Optimal" : "Suboptimal" }),
        ),
        h("p", { text: `Pieces still hidden: ${step.turn.remaining.join(", ") || "none"}` }),
        step.placed_cells === undefined
          ? grid(step.board, "Board after drop")
          : h("div", { class: "tetris-boards" },
            dropPanel("AI drop", "ai-drop", step.turn, step.move, step.placed_cells, step.submitted_score),
            dropPanel(matched ? "Same drop is optimal" : "One optimal drop", "best-drop", step.turn,
              step.optimal_move ?? step.move, step.optimal_cells, step.optimal_score),
          ),
        h("p", { text: `Rows cleared by the AI: ${step.cleared}` }),
      );
    })),
  );
}

function agentMove(value, { verdict }) {
  if (!["optimal", "suboptimal"].includes(verdict.details.status)) {
    return h("p", { text: verdict.message });
  }
  return h("section", {}, h("p", { text: moveLabel(value) }), outcome(verdict.details));
}

export default { GameOutput: game, MoveOutput: agentMove };
