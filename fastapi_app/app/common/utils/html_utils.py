from bs4 import BeautifulSoup


# 스크랩한 기사 제목에서 HTML 태그를 제거하고 텍스트만 추출
def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()


# 스크랩한 기사 본문에서 불필요한 태그 제거 후 텍스트 정제
def clean_article_content(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style", "aside", "footer", "header", "nav", "form"]):
        tag.decompose()

    article_body = soup.find("article") or soup.find("div", class_="content") or soup
    text = article_body.get_text(separator="\n")
    clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return clean_text