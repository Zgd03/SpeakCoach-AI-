"""Evaluation utilities for tracking scores across a session."""


class ScoreTracker:
    """Tracks per-dimension scores across multiple turns and computes averages."""

    def __init__(self):
        self.grammar_scores: list[float] = []
        self.fluency_scores: list[float] = []
        self.vocabulary_scores: list[float] = []

    def add_turn(self, grammar: float, fluency: float, vocabulary: float):
        self.grammar_scores.append(grammar)
        self.fluency_scores.append(fluency)
        self.vocabulary_scores.append(vocabulary)

    @property
    def average_grammar(self) -> float:
        return _avg(self.grammar_scores)

    @property
    def average_fluency(self) -> float:
        return _avg(self.fluency_scores)

    @property
    def average_vocabulary(self) -> float:
        return _avg(self.vocabulary_scores)

    @property
    def overall(self) -> float:
        scores = [
            self.average_grammar,
            self.average_fluency,
            self.average_vocabulary,
        ]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 1)

    def to_dict(self) -> dict:
        return {
            "grammar": self.average_grammar,
            "fluency": self.average_fluency,
            "vocabulary": self.average_vocabulary,
        }


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)
