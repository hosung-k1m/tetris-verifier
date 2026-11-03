import { h } from "./kit/components.js";

const shapes = {
  I: ["####"], J: ["#..", "###"], L: ["..#", "###"], O: ["##", "##"],
  S: [".##", "##."], T: [".#.", "###"], Z: ["##.", ".##"],
};

function grid(rows, label) {
  return h("div", {
    class: "tetris-grid", role: "img", "aria-label": label,
    style: `grid-template-columns: repeat(${rows[0].length}, minmax(0, 1fr))`,
  }, rows.flatMap(row => [...row].map(cell => h("span", { class: cell === "#" ? "filled" : "empty" }))));
}

function piece(name) {
  return h("div", { class: "tetris-piece" }, h("span", { text: name }), grid(shapes[name], `${name} shape`));
}

function turnHeader(turn) {
  return h("section", { class: "tetris-turn" },
    grid(turn.board, "Starting board"),
    h("div", {},
      h("h4", { text: "Current piece" }), piece(turn.current),
      h("h4", { text: "Remaining pieces (unordered)" }),
      turn.remaining.length ? h("div", { class: "tetris-bag" }, [...turn.remaining].sort().map(piece))
        : h("p", { text: "None" }),
    ),
  );
}

const moveLabel = move => `${90 * move.orientation}° clockwise · column ${move.column + 1}`;
const scoreLabel = score => score === 81 ? "Top-out (81)" : `${score} cells left`;

function openPuzzle(value, { verdict, send }) {
  if (!verdict.valid) return h("p", { text: verdict.message });
  const { turn, placements } = value;
  const label = h("label", { text: "Placement" });
  const select = h("select", { "aria-label": "Placement" }, placements.map(({ move, top_out }, i) =>
    h("option", { value: String(i), text: moveLabel(move) + (top_out ? " · top-out" : "") })));
  label.append(select);
  const preview = h("div");
  function draw() {
    const drop = placements[Number(select.value)];
    preview.replaceChildren(
      h("p", { text: drop.top_out ? "Top-out: the piece cannot enter." : `Rows cleared: ${drop.cleared}` }),
      grid(drop.board, "Board after the drop"),
    );
  }
  select.addEventListener("change", draw);
  draw();
  const commit = h("button", { type: "button", class: "button primary", text: "Commit drop" });
  commit.addEventListener("click", () => {
    const player = placements[Number(select.value)].move;
    select.disabled = commit.disabled = true;
    commit.textContent = "Drop committed";
    send(`Committed turn: ${JSON.stringify({ turn, player })}. Run choose-optimal-move with only the turn. Then run compare-moves with the unchanged turn, my committed player move, and the exact agent submission, even if its verdict failed. Show the comparison in Result.`);
  });
  return h("section", {}, turnHeader(turn), label, preview, commit);
}

function outcome(title, move, graded) {
  const section = h("section", {}, h("h4", { text: title }));
  if (graded.status === "illegal_move") {
    section.append(h("p", { text: `Illegal placement (orientation ${move.orientation}, column index ${move.column}).` }));
    return section;
  }
  section.append(
    h("p", { text: moveLabel(move) }),
    h("p", { text: graded.status === "optimal" ? "Optimal placement" : "A better placement exists" }),
    h("p", { text: `Worst outcome: ${scoreLabel(graded.submitted_score)}` }),
    h("p", { text: `Best possible: ${scoreLabel(graded.optimal_score)}` }),
  );
  if (graded.replay) {
    section.append(h("details", {},
      h("summary", { text: "Replay the worst reveal order" }),
      h("ol", {}, graded.replay.map(step => h("li", {},
        h("p", { text: `${step.piece} · ${moveLabel(step.move)} · ${step.top_out ? "top-out" : `${step.cleared} rows cleared`}` }),
        grid(step.board, `Board after ${step.piece}`),
      ))),
    ));
  }
  return section;
}

function agentMove(value, { verdict }) {
  return verdict.details.status === "malformed_turn" ? h("p", { text: verdict.message })
    : outcome("Agent", value, verdict.details);
}

function comparison(value, { verdict, send }) {
  if (!verdict.valid) return h("p", { text: verdict.message });
  return h("section", {}, turnHeader(value.turn),
    h("div", { class: "tetris-outcomes" },
      outcome("You", value.player, verdict.details.player),
      outcome("Agent", value.agent, verdict.details.agent),
    ),
    ...["split", "stack"].map(puzzle => h("button", {
      type: "button", class: "button", text: `Play ${puzzle}`,
      onclick: () => send(`Run start-puzzle with puzzle ${puzzle}.`),
    })),
  );
}

export default { PuzzleOutput: openPuzzle, MoveOutput: agentMove, CompareOutput: comparison };
