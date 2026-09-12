from bottle import route, run, template, request, redirect

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    label = request.query.get("label")
    news_id = request.query.get("id")
    s = session()
    news = s.query(News).get(news_id)
    if news:
        news.label = label
    s.commit()
    if __name__ == "__main__":
        redirect("/news")


@route("/update")
def update_news():
    fresh = get_news("https://habr.com/ru/articles/", n_pages=1)
    s = session()
    for item in fresh:
        exists = s.query(News).filter(News.title == item["title"], News.author == item["author"]).first()
        if not exists:
            n = News(
                title=item["title"],
                author=item["author"],
                url=item.get("url", item.get("link", "")),
                complexity=item["complexity"],
                habr_id=item.get("id", ""),
            )
            s.add(n)
            s.commit()
    s.close()
    if __name__ == "__main__":
        redirect("/news")


@route("/recommendations")
def recommendations():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    labeled = s.query(News).filter(News.label != None).all()
    X_train = [f"{r.title} {r.author} {r.complexity}" for r in labeled]
    y_train = [r.label for r in labeled]
    X_test = [f"{r.title} {r.author} {r.complexity}" for r in rows]
    clf = NaiveBayesClassifier(alpha=0.05)
    clf.fit(X_train, y_train)
    predictions = clf.predict(X_test)
    order = {"good": 0, "maybe": 1, "never": 2}
    classified_news = sorted(zip(rows, predictions), key=lambda x: order.get(x[1], 3))
    s.close()
    return template("news_recommendations", rows=classified_news)


@route("/classify")
def classify_news():
    s = session()
    labeled = s.query(News).filter(News.label != None).all()
    rows = s.query(News).filter(News.label == None).all()

    X_train = [f"{r.title} {r.author} {r.complexity}" for r in labeled]
    y_train = [r.label for r in labeled]
    X_test = [f"{r.title} {r.author} {r.complexity}" for r in rows]

    clf = NaiveBayesClassifier(alpha=0.05)
    clf.fit(X_train, y_train)
    predictions = clf.predict(X_test)

    order = {"good": 0, "maybe": 1, "never": 2}
    classified_news = sorted(zip(rows, predictions), key=lambda x: order.get(x[1], 3))

    s.close()
    return [n for n, label in classified_news]


if __name__ == "__main__":
    run(host="localhost", port=8080)
