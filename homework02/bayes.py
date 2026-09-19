import math
import re
from collections import Counter, defaultdict


class NaiveBayesClassifier:

    def __init__(self, alpha=0.01):
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        self.alpha = alpha
        self.classes_ = []
        self.class_counts_ = Counter()
        self.word_counts_ = defaultdict(Counter)
        self.total_words_ = Counter()
        self.vocabulary_ = set()
        self.fitted_ = False

    @staticmethod
    def _tokenize(document):
        if not isinstance(document, str):
            document = str(document)
        return re.findall(r"\b[\w'-]+\b", document.lower(), flags=re.UNICODE)

    def fit(self, X, y):
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        if not X:
            raise ValueError("training data must not be empty")

        self.class_counts_.clear()
        self.word_counts_.clear()
        self.total_words_.clear()
        self.vocabulary_.clear()

        for document, target in zip(X, y):
            self.class_counts_[target] += 1
            words = self._tokenize(document)
            self.word_counts_[target].update(words)
            self.total_words_[target] += len(words)
            self.vocabulary_.update(words)

        self.classes_ = list(self.class_counts_.keys())
        self.fitted_ = True
        return self

    def _predict_one(self, document):
        if not self.fitted_:
            raise ValueError("classifier is not fitted")

        words = self._tokenize(document)
        vocabulary_size = len(self.vocabulary_)
        n_documents = sum(self.class_counts_.values())

        scores = {}
        for target in self.classes_:
            score = math.log(self.class_counts_[target] / n_documents)
            denominator = self.total_words_[target] + self.alpha * vocabulary_size

            for word in words:
                if word not in self.vocabulary_:
                    continue
                probability = (
                    self.word_counts_[target][word] + self.alpha
                ) / denominator
                score += math.log(probability)

            scores[target] = score

        return max(scores, key=scores.get)

    def predict(self, X):
        return [self._predict_one(document) for document in X]

    def score(self, X_test, y_test):
        if len(X_test) != len(y_test):
            raise ValueError("X_test and y_test must have the same length")
        if not y_test:
            return 0.0

        predictions = self.predict(X_test)
        return round(
            sum(pred == actual for pred, actual in zip(predictions, y_test)) / len(y_test),
            12,
        )