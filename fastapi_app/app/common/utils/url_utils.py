from urllib.parse import urlparse


def get_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def is_naver_blog(url: str) -> bool:
    return get_domain(url) == "blog.naver.com"


def is_naver_news(url: str) -> bool:
    return get_domain(url) == "news.naver.com"


def join_url(*parts: str) -> str:
    """
    URL 파트들을 안전하게 결합하여 단일 URL 문자열로 반환합니다.
    슬래시 중복을 제거하고, 누락된 슬래시를 자동 정리하며,
    마지막에는 항상 슬래시(`/`)를 유지합니다.

    예:
        join_url("http://localhost:8000", "/api/keywords/", "list/")
        -> "http://localhost:8000/api/keywords/list/"
    """
    return "/".join(part.strip("/") for part in parts) + "/"
