# fastapi_app/app/features/internal/generate_clova_post/prompt_builder.py

def build_prompt(title: str, article_content: str) -> str:
    """
    Clova Studio 튜닝 모델 요청용 프롬프트 생성
    - title: Keyword.title (키워드)
    - article_content: 기사 본문
    """
    return f"""기사 내용을 참고해(재창출 필수) 6단락 블로그 글을 작성해주세요.  
각 단락은 소제목을 포함하고, 공백 제외 3,000자 이상이어야 합니다.  
제목은 키워드 원형을 그대로 앞에 두고, 자연스럽게 이어지는 롱테일 문장으로 작성해주세요.  
키워드는 띄어쓰기·기호 포함 그대로 사용하며, 키워드와 이어지는 문장 사이에는 기호나 부호 삽입을 금지합니다.  
글 전체는 친근하면서도 전문적인 말투로 구성하고, 마지막 단락에는 독자에게 질문 2개를 포함해주세요.

[키워드]
{title}

[기사 본문]
{article_content}
"""
