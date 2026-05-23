"""Tiny built-in character model for language-like filler text."""

import math
import random
from typing import List


TINY_LANGUAGE_CORPUS = (
    "Файл містить текстові дані для перевірки обробки. "
    "Користувач вибирає папку, задає розмір і запускає процес. "
    "Система читає документ, змінює вміст і записує результат. "
    "Параметр розміру допомагає підготувати однакові файли. "
    "Операція створює приклад технічного тексту для тестування. "
    "Рядок містить слова, пробіли, символи та прості речення. "
)


class TinyCharacterModel:
    """A very small single-layer character language model.

    The model uses one-hot previous-character features and learned transition
    logits from the embedded corpus. It is intentionally tiny and dependency-free.
    """

    def __init__(self, corpus: str = TINY_LANGUAGE_CORPUS) -> None:
        self._vocabulary = sorted(set(corpus))
        self._index = {char: index for index, char in enumerate(self._vocabulary)}
        self._bias_logits = []  # type: List[float]
        self._prev_logits = []  # type: List[List[float]]
        self._prev2_logits = []  # type: List[List[float]]
        self._train(corpus)

    def generate(self, minimum_bytes: int, seed: str = "Файл ") -> str:
        """Generate language-like text with at least the requested UTF-8 bytes."""

        if minimum_bytes <= 0:
            return ""

        output = list(seed)
        while len("".join(output).encode("utf-8")) < minimum_bytes:
            output.append(self._sample_next(output))
        return "".join(output)

    def _train(self, corpus: str) -> None:
        size = len(self._vocabulary)
        bias_counts = [1.0] * size
        prev_counts = [[1.0] * size for _ in range(size)]
        prev2_counts = [[1.0] * size for _ in range(size)]

        for position, char in enumerate(corpus):
            char_index = self._index[char]
            bias_counts[char_index] += 1.0
            if position >= 1:
                prev_counts[self._index[corpus[position - 1]]][char_index] += 1.0
            if position >= 2:
                prev2_counts[self._index[corpus[position - 2]]][char_index] += 0.5

        self._bias_logits = self._counts_to_logits(bias_counts)
        self._prev_logits = [self._counts_to_logits(row) for row in prev_counts]
        self._prev2_logits = [self._counts_to_logits(row) for row in prev2_counts]

    def _counts_to_logits(self, counts: List[float]) -> List[float]:
        total = sum(counts)
        return [math.log(count / total) for count in counts]

    def _sample_next(self, output: List[str]) -> str:
        previous = output[-1] if output else " "
        previous2 = output[-2] if len(output) >= 2 else " "
        previous_index = self._index.get(previous, self._index[" "])
        previous2_index = self._index.get(previous2, self._index[" "])

        scores = [
            (0.15 * bias) + self._prev_logits[previous_index][index] + (0.35 * self._prev2_logits[previous2_index][index])
            for index, bias in enumerate(self._bias_logits)
        ]
        max_score = max(scores)
        weights = [math.exp(score - max_score) for score in scores]
        return random.choices(self._vocabulary, weights=weights, k=1)[0]


DEFAULT_TEXT_MODEL = TinyCharacterModel()


def generate_language_like_padding(size_bytes: int) -> bytes:
    """Generate exact-size UTF-8 bytes from the tiny character model."""

    if size_bytes <= 0:
        return b""

    data = DEFAULT_TEXT_MODEL.generate(size_bytes).encode("utf-8")
    while len(data) < size_bytes:
        data += DEFAULT_TEXT_MODEL.generate(size_bytes - len(data), seed=" ").encode("utf-8")

    if len(data) == size_bytes:
        return data

    truncated = data[:size_bytes].decode("utf-8", errors="ignore").encode("utf-8")
    if len(truncated) < size_bytes:
        truncated += b" " * (size_bytes - len(truncated))
    return truncated
