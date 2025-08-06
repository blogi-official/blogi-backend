import time

from app.common.logger import get_logger

logger = get_logger(__name__)


def convert_to_html_paragraphs(text: str) -> str:
    """
    단락을 <p> 태그로 감싸서 HTML 형식으로 변환
    """
    paragraphs = text.strip().split("\n\n")
    return "\n".join(f"<p>{para.strip()}</p>" for para in paragraphs)


async def generate_clova_post(title: str, content: str) -> dict:
    """
    Clova Studio API를 호출하여 블로그 콘텐츠를 생성합니다.
    이미지 삽입 없이 HTML 텍스트만 반환합니다.
    (이미지 삽입은 service.py 쪽에서 후처리로 담당)
    """

    start_time = time.time()

    try:
        logger.info(f"[Clova] 콘텐츠 생성 시작 - title: {title}")
        logger.debug(f"[Clova] 원문 content[:100]: {content[:100]}...")

        # TODO: Clova Studio 실제 호출 로직 추가 필요
        # 현재는 mock 결과 사용
        raw_text = f"[블로그 자동 생성]\n\n{content}\n\n#자동생성 #Clova"
        html_content = convert_to_html_paragraphs(raw_text)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "success",
            "title": title,
            "content": html_content,
            "response_time_ms": elapsed_ms,
        }

    except Exception as e:
        logger.error(f"[Clova] 생성 실패 - {e}", exc_info=True)
        return {"status": "fail", "error_message": str(e)}
