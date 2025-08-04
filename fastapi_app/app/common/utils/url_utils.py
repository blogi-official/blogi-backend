from urllib.parse import urlparse


def get_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def is_naver_blog(url: str) -> bool:
    return get_domain(url) == "blog.naver.com"


def is_naver_news(url: str) -> bool:
    return get_domain(url) == "news.naver.com"
