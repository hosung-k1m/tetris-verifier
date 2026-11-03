"""Exact adversarial reveal search; the response to a reveal sees only the remaining set."""

from functools import cache

from contract import MoveOutput

from .rules import TOP_OUT, WIDTH, drop, legal, moves, pack, unpack


def grade(turn, *submissions):
    def after_move(board, piece, remaining, orientation, column):
        after, _ = drop(board, piece, orientation, column)
        if after is None:
            return TOP_OUT
        if not remaining:
            return after.bit_count()
        return max(best(after, reveal, rest)[0] for reveal, rest in reveals(remaining))

    @cache
    def best(board, piece, remaining):
        score = TOP_OUT + 1
        bound = (board.bit_count() + 4 * (1 + len(remaining))) % WIDTH
        for orientation, column in moves(piece):
            candidate = after_move(board, piece, remaining, orientation, column)
            if candidate < score:
                score, selected = candidate, (orientation, column)
                if score == bound:
                    break
        return score, selected

    def replay(board, piece, remaining, move):
        after, cleared = drop(board, piece, *move)
        yield {
            "piece": piece,
            "move": MoveOutput(*move),
            "cleared": cleared,
            "board": unpack(board if after is None else after),
            "top_out": after is None,
        }
        if after is not None and remaining:
            _, next_piece, rest, response = max(
                (
                    (best(after, reveal, rest)[0], reveal, rest, best(after, reveal, rest)[1])
                    for reveal, rest in reveals(remaining)
                ),
                key=lambda option: option[0],
            )
            yield from replay(after, next_piece, rest, response)

    board, piece, remaining = pack(turn.board), turn.current, tuple(sorted(turn.remaining))
    try:
        optimal, _ = best(board, piece, remaining)
        results = []
        for move in submissions:
            if not legal(piece, move):
                results.append({"status": "illegal_move", "optimal_score": optimal})
                continue
            selected = (move.orientation, move.column)
            score = after_move(board, piece, remaining, *selected)
            result = {
                "status": "optimal" if score == optimal else "suboptimal",
                "submitted_score": score,
                "optimal_score": optimal,
            }
            if score != optimal:
                result["replay"] = list(replay(board, piece, remaining, selected))
            results.append(result)
        return results
    finally:
        best.cache_clear()


def reveals(remaining):
    for index, piece in enumerate(remaining):
        yield piece, remaining[:index] + remaining[index + 1 :]
