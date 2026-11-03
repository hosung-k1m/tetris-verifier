import { h } from "./kit/components.js";

function grid(rows, label) {
  return h("div", { class: "tetris-grid", role: "img", "aria-label": label },
    rows.flatMap(row => [...row].map(cell => h("span", { class: cell === "#" ? "filled" : "empty" }))));
}

const moveLabel = move => `${90 * move.orientation}° clockwise · column ${move.column + 1}`;
const scoreLabel = score => score === 81 ? "Top-out (81)" : `${score} cells left`;

function outcome(graded) {
  return [
    h("p", { text: graded.status === "optimal" ? "Optimal placement" : "Suboptimal placement" }),
    h("p", { text: `Worst outcome: ${scoreLabel(graded.submitted_score)} · Best possible: ${scoreLabel(graded.optimal_score)}` }),
  ];
}

function game(_value, { verdict, send }) {
  const moves = verdict.details.moves;
  return h("section", {},
    h("p", { text: verdict.message }),
    h("ol", { class: "tetris-moves" }, moves.map((step, index) => h("li", {},
      h("h4", { text: `Move ${index + 1}: ${step.turn.current} · ${moveLabel(step.move)}` }),
      h("p", { text: `Remaining before placement: ${step.turn.remaining.join(", ") || "none"}` }),
      outcome(step),
      h("div", { class: "tetris-boards" },
        h("div", {}, h("p", { text: "Before drop" }), grid(step.turn.board, "Board before drop")),
        h("div", {}, h("p", { text: step.top_out ? "Top-out" : `Rows cleared: ${step.cleared}` }),
          grid(step.board, "Board after drop")),
      ),
    ))),
    ...["stack", "split"].map(puzzle => h("button", {
      type: "button", class: "button", text: `Watch ${puzzle}`,
      onclick: () => send(`Run play-puzzle with puzzle ${puzzle}.`),
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
