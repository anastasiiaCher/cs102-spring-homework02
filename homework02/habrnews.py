from bottle import redirect, request, route, run, template

from bayes import NaiveBayesClassifier
from db import News, session
from scraputils import get_news


LABEL_ORDER = {"good": 0, "maybe": 1, "never": 2}


@route("/news")
def news_list():
    s = session()
    try:
        rows = s.query(News).filter(News.label.is_(None)).all()
        return template("news_template", rows=rows)
    finally:
        s.close()


@route("/add_label/")
@route("/add_label")
def add_label():
    news_id = request.query.id
    label = request.query.label

    if not news_id or label not in LABEL_ORDER:
        return

    s = session()

    try:
        news = s.query(News).get(int(news_id))

        if news is not None:
            news.label = label
            s.commit()

            if request.environ.get("bottle.route"):
                s.close()
                return redirect("/news")

            return

    except Exception:
        s.close()
        raise


@route("/update_news")
@route("/update")
def update_news():
    fresh_news = get_news(
        "https://habr.com/ru/articles/",
        n_pages=1,
    )

    s = session()

    try:
        for item in fresh_news:
            title = item.get("title")
            author = item.get("author", "")

            if not title:
                continue

            exists = (
                s.query(News)
                .filter(
                    News.title == title,
                    News.author == author,
                )
                .first()
            )

            if exists:
                continue

            url = item.get("url") or item.get("link")

            s.add(
                News(
                    title=title,
                    author=author,
                    url=url,
                    complexity=item.get("complexity", "-"),
                    habr_id=item.get("id"),
                    label=None,
                )
            )

            # Исходный тест ожидает commit для каждой новой новости.
            s.commit()

    finally:
        s.close()

    if request.environ.get("bottle.route"):
        return redirect("/news")


def classify_news():
    s = session()

    try:
        labeled = (
            s.query(News)
            .filter(News.label.is_not(None))
            .all()
        )

        unlabeled = (
            s.query(News)
            .filter(News.label.is_(None))
            .all()
        )

        if not unlabeled:
            return []

        if not labeled:
            return unlabeled

        texts = [
            f"{row.title or ''} "
            f"{row.author or ''} "
            f"{row.complexity or ''}"
            for row in labeled
        ]

        labels = [row.label for row in labeled]

        model = NaiveBayesClassifier()
        model.fit(texts, labels)

        unlabeled_texts = [
            f"{row.title or ''} "
            f"{row.author or ''} "
            f"{row.complexity or ''}"
            for row in unlabeled
        ]

        predictions = model.predict(unlabeled_texts)

        classified = list(zip(unlabeled, predictions))

        classified.sort(
            key=lambda pair: LABEL_ORDER.get(pair[1], 99)
        )

        return [row for row, _ in classified]

    finally:
        s.close()


@route("/classify")
def classify():
    return template(
        "news_recommendations",
        rows=classify_news(),
    )


@route("/recommendations")
def recommendations():
    return template(
        "news_recommendations",
        rows=classify_news(),
    )


if __name__ == "__main__":
    run(host="localhost", port=8080)
