from konlpy.tag import Okt

okt = Okt()  # 전역에서 재사용 가능


def is_valid_blog_content(content: str, keyword: str, min_length: int = 300) -> bool:
    """본문이 충분히 길고 키워드와 관련된 내용을 포함하는지 판단"""
    if len(content.strip()) < min_length:
        return False

    content_nouns = set(okt.nouns(content))
    keyword_nouns = set(okt.nouns(keyword))

    if not content_nouns & keyword_nouns:
        return False

    return True
