import random
import re
from collections import defaultdict


class MarkovModel:
    def __init__(self, order=3):
        self.order = order
        self.chain = defaultdict(list)
        self.starters = []
        self._vocab = set()

    def _tokenize(self, text: str) -> list:
        text = text.lower().strip()
        tokens = re.findall(r'\w+|[.,!?;:]', text)
        return tokens

    def train(self, text: str):
        tokens = self._tokenize(text)
        if len(tokens) < self.order + 1:
            return

        self._vocab.update(tokens)

        # Запоминаем начала предложений
        self.starters.append(tuple(tokens[:self.order]))

        for i in range(len(tokens) - self.order):
            key = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            self.chain[key].append(next_word)

    def generate(self, seed: str = None, max_words: int = 30) -> str:
        if not self.chain:
            return None

        # Выбираем стартовый ключ
        if seed:
            seed_tokens = self._tokenize(seed)
            # Ищем ключ связанный с seed
            matching = [k for k in self.chain.keys()
                       if any(w in k for w in seed_tokens)]
            if matching:
                current = random.choice(matching)
            else:
                current = random.choice(self.starters) if self.starters else random.choice(list(self.chain.keys()))
        else:
            current = random.choice(self.starters) if self.starters else random.choice(list(self.chain.keys()))

        result = list(current)

        for _ in range(max_words - self.order):
            key = tuple(result[-self.order:])
            if key not in self.chain:
                break
            next_word = random.choice(self.chain[key])
            result.append(next_word)

            # Останавливаемся на знаках препинания
            if next_word in '.!?' and len(result) > 8:
                break

        if not result:
            return None

        # Собираем текст
        text = ' '.join(result)
        text = re.sub(r' ([.,!?;:])', r'\1', text)
        return text.capitalize()

    def vocab_size(self) -> int:
        return len(self._vocab)
