# app/common/constants/playwright_selectors.py

# 뉴스 도메인별 selector 매핑
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
    "topstarnews.net": "#dic_area",  # 탑스타뉴스
    "sedaily.com": "#v-left-scroll-in",  # 서울경제
    "esquirekorea.co.kr": ".article-view",  # 에스콰이어
    "xportsnews.com": "#newsContent",  # 엑스포츠뉴스
    "newsen.com": "#news_body_area",  # 뉴스엔
    "doctorsnews.co.kr": "div.view_con",  # 의사신문
    # 필요 시 확장
}

# 뉴스 기본 selector (도메인 미매칭 시)
DEFAULT_SELECTORS = [
    "#dic_area",
    "article",
    ".article",
    ".view",
    "#articleBodyContents",
    "div.article-content",
    "div#content",
]

BLOG_DOMAIN_SELECTOR_MAP = {
    "blog.naver.com": [
        "div.se-viewer",  # 최신 에디터
        "div.se-main-container",  # 모바일
        "div#postViewArea",  # 구형 에디터
    ]
}

BLOG_DEFAULT_SELECTORS = [
    "div.se-viewer",
    "div.se-main-container",
    "div#postViewArea",
]
