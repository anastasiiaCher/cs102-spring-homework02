import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://habr.com"
START_URL = f"{BASE_URL}/ru/articles/"


def _text(node):
    return node.get_text(" ", strip=True) if node else ""


def _find_first(node, selectors):
    for selector in selectors:
        result = node.select_one(selector)
        if result:
            return result
    return None


def extract_news(parser):
    news_list = []

    articles = parser.select("article.tm-articles-list__item")
    if not articles:
        articles = parser.find_all("article")

    for article in articles:
        title_node = _find_first(
            article,
            [
                "a.tm-title__link",
                "a.tm-article-snippet__title-link",
                "h2 a",
            ],
        )
        if not title_node:
            continue

        title = _text(title_node)
        link = urljoin(BASE_URL, title_node.get("href", ""))

        author_node = _find_first(
            article,
            [
                "a.tm-user-info__username",
                ".tm-user-info__username",
                "a.tm-article-snippet__author",
            ],
        )
        author = _text(author_node)

        complexity_node = _find_first(
            article,
            [
                "span.tm-article-complexity__label",
                ".tm-article-complexity__label",
            ],
        )
        complexity = _text(complexity_node) or "-"

        habr_id = None
        article_id = article.get("id", "")
        match = re.search(r"(\d+)", article_id)
        if match:
            habr_id = match.group(1)

        if not habr_id:
            match = re.search(r"/(?:articles|post|news)/(\d+)", link)
            if match:
                habr_id = match.group(1)

        news_list.append(
            {
                "author": author,
                "complexity": complexity,
                "id": habr_id,
                "link": link,
                "title": title,
            }
        )

    return news_list


def extract_next_page(parser):
    # Актуальная пагинация Habr.
    selectors = [
        "a.tm-pagination__next",
        "a.tm-pagination__button_next",
        "a[data-test-id='pagination-next']",
        "a[rel='next']",
    ]

    for selector in selectors:
        node = parser.select_one(selector)
        if node and node.get("href"):
            return node["href"]

    # Ищем ссылку на следующую страницу по атрибутам.
    for node in parser.find_all("a", href=True):
        href = node["href"]
        text = _text(node).strip().lower()
        aria = (node.get("aria-label") or "").strip().lower()
        title = (node.get("title") or "").strip().lower()

        if (
            "next" in text
            or "next" in aria
            or "next" in title
            or "следующ" in text
            or "следующ" in aria
            or "следующ" in title
        ):
            return href

    # Если кнопка не имеет текста, ищем ссылки пагинации.
    pagination_links = parser.select(
        "nav a[href*='page'], "
        ".tm-pagination a[href*='page'], "
        "a[href*='page=']"
    )

    for node in pagination_links:
        href = node.get("href", "")
        if href and "page=" in href:
            return href

    return None


def get_news(url=START_URL, n_pages=1):
    news = []

    for _ in range(n_pages):
        print(f"Collecting data from page: {url}")

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_news = extract_news(soup)
        news.extend(page_news)

        print(f"  На странице найдено: {len(page_news)}")

        next_page = extract_next_page(soup)

        if not next_page:
            print("  Следующая страница не найдена.")
            break

        url = urljoin(BASE_URL, next_page)

    return news
