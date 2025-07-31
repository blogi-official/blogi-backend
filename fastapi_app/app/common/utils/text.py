import re


def extract_first_word(title: str) -> str:
    """
    제목에서 쉼표(,), 공백 등을 기준으로 첫 번째 주요 단어 추출
    - ♥, · 등의 연결 문자는 유지 (고유명사 판단)

    예:
    - "오타니, 맞대결 참교육 현장" → "오타니"
    - "류승범♥공효진 결혼발표" → "류승범♥공효진"
    - "서장훈·이수근 폭로" → "서장훈·이수근"
    """
    # 1. 쉼표 기준 분리
    parts = title.split(",")
    first_chunk = parts[0].strip()

    # 2. 공백 기준 추가 분리
    space_split = first_chunk.split()
    return space_split[0] if space_split else first_chunk
