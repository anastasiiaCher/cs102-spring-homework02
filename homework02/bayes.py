from collections import Counter, defaultdict
import math


class NaiveBayesClassifier:

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = None
        self.class_priors = {}
        self.word_probs = {}
        self.vocab = set()

    def fit(self, X, y):
        """Fit Naive Bayes classifier according to X, y."""
        self.classes = set(y)
        class_counts = Counter(y)
        total = len(y)
        self.class_priors = {c: class_counts[c] / total for c in self.classes}
        word_counts = {c: Counter() for c in self.classes}
        total_words = {c: 0 for c in self.classes}
        for text, cls in zip(X, y):
            words = text.split()
            for w in words:
                word_counts[cls][w] += 1
                total_words[cls] += 1
                self.vocab.add(w)
        d = len(self.vocab)
        self.word_probs = {}
        for cls in self.classes:
            self.word_probs[cls] = {}
            for w in self.vocab:
                self.word_probs[cls][w] = (word_counts[cls][w] + self.alpha) / (total_words[cls] + self.alpha * d)

    def predict(self, X):
        """Perform classification on an array of test vectors X."""
        predictions = []
        for text in X:
            words = text.split()
            scores = {}
            for cls in self.classes:
                score = math.log(self.class_priors[cls])
                for w in words:
                    if w in self.vocab:
                        score += math.log(self.word_probs[cls][w])
                scores[cls] = score
            predictions.append(max(scores, key=scores.get))
        return predictions

    def score(self, X_test, y_test):
        """Returns the mean accuracy on the given test data and labels."""
        predictions = self.predict(X_test)
        correct = sum(1 for p, t in zip(predictions, y_test) if p == t)
        return correct / len(y_test)
