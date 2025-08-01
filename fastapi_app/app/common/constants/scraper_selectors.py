# news
DOMAIN_SELECTOR_MAP = {
    "news.naver.com": "#dic_area",  # 네이버 뉴스
    "sportsseoul.com": "article",  # 스포츠서울
    "iminju.net": "article",  # 민주신문
    "joongang.co.kr": "div#article_body",  # 중앙일보
    "hani.co.kr": "div.article-text",  # 한겨레
    "yna.co.kr": "div#content-text",  # 연합뉴스
    "donga.com": "div.article_txt",  # 동아일보
    "chosun.com": "div#news_body_id",  # 조선일보
    "mk.co.kr": "div.article",  # 매일경제
    "ohmynews.com": "div.article-content",  # 오마이뉴스
    "edaily.co.kr": "div#contents",  # 이데일리
    "newsis.com": "div.article_body",  # 뉴시스
    "cnbnews.com": "div.article",  # CNB뉴스
    # 필요시 추가 가능
}


DEFAULT_SELECTORS = ["article", "div.article-content", "div#content"]


# blog
BLOG_DOMAIN_SELECTOR_MAP = {
    "blog.naver.com": "div.se-viewer",
    "m.blog.naver.com": "div.se-main-container",
    # 필요시 추가 가능
}


# 블로그 본문용 기본 선택자 예시 (네이버 모바일 블로그 기준)
BLOG_DEFAULT_SELECTORS = [
    "div.se-viewer",  # 네이버 블로그 본문 전체 컨테이너 추가
    "div.se-main-container",  # 기존 네이버 모바일 본문 컨테이너
    "div#postViewArea",  # PC 버전 블로그 본문 영역
]
