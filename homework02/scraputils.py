import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """Extract news from a given web page"""
    news_list = []
    articles = parser.find_all("article", class_="tm-articles-list__item")
    for article in articles:
        title_tag = article.find("a", class_="tm-title__link")
        title = title_tag.text.strip() if title_tag else "No title"
        link = "https://habr.com" + title_tag.get("href") if title_tag else ""
        habr_id = link.rstrip("/").split("/")[-1] if link else ""
        author_tag = article.find("a", class_="author")
        author = author_tag.text.strip() if author_tag else "Unknown"
        complexity_tag = article.find("span", class_="tm-article-complexity__label")
        complexity = complexity_tag.text.strip() if complexity_tag else "-"
        news_list.append(
            {
                "title": title,
                "author": author,
                "link": link,
                "complexity": complexity,
                "id": habr_id,
            }
        )
    return news_list


def extract_next_page(parser):
    """Extract next page URL"""
    next_btn = parser.find("a", id="pagination-next-page")
    if next_btn:
        return next_btn.get("href")
    return None


def get_news(url, n_pages=1):
    """Collect news from a given web page"""
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://habr.com" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
