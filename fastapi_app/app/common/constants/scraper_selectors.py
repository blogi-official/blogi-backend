# 도메인별 selector 매핑
DOMAIN_SELECTOR_MAP = {
    "topstarnews.net": "#dic_area",
    "sedaily.com": "#v-left-scroll-in",
    "esquirekorea.co.kr": ".article-view",
    "xportsnews.com": "#newsContent",
    "edaily.co.kr": "#newsContent",
    "newsen.com": "#news_body_area",
    "doctorsnews.co.kr": "div.view_con",
}

# 기본 selector 리스트 (매핑 실패 시 사용)
DEFAULT_SELECTORS = [
    "#dic_area",
    "article",
    ".article",
    ".view",
    "#articleBodyContents",
]
