import re
import time
from urllib.parse import quote
from uuid import uuid4

import httpx

from app.common.logger import get_logger
from app.core.config import settings
from app.features.internal.generate_clova_post.prompt_builder import build_prompt

logger = get_logger(__name__)


def convert_to_html_paragraphs(text: str, image_urls: list[str]) -> str:
    """
    Clova 응답을 HTML로 변환
    - '**소제목**' 형식을 <h3>로 인식
    - 그 아래 문장은 <p>
    - 각 단락마다 이미지 삽입 (최대 3개)
    """
    paragraphs = []
    lines = text.strip().split("\n")
    current_subtitle = None
    current_body = []
    image_idx = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        subtitle_match = re.match(r"\*\*(.+?)\*\*", line)
        if subtitle_match:
            if current_subtitle and current_body:
                paragraphs.append((current_subtitle, " ".join(current_body)))
                current_body = []
            current_subtitle = subtitle_match.group(1)
        else:
            current_body.append(line)

    if current_subtitle and current_body:
        paragraphs.append((current_subtitle, " ".join(current_body)))

    html_parts = []
    for idx, (subtitle, body) in enumerate(paragraphs):
        img_html = ""
        if image_idx < len(image_urls):

            proxy_url = (
                f"{settings.fastapi_origin}/api/v1/internal/proxy-image?url={quote(image_urls[image_idx], safe='')}"
            )
            img_html = (
                f'<img src="{proxy_url}" alt="대표 이미지 {image_idx + 1}" style="max-width:100%; margin: 1rem 0;" />'
            )
            image_idx += 1
        html_parts.append(f"<h3>{subtitle}</h3>\n{img_html}\n<p>{body}</p>")

    return "\n".join(html_parts)


async def generate_clova_post(title: str, article_content: str, image_urls: list[str]) -> dict:
    """
    Clova Studio 튜닝 모델을 호출하여 블로그 콘텐츠 생성
    - 응답 첫 줄: 제목
    - 나머지: 본문 (HTML 단락 구성 포함)
    - <h1> 제목 + <h3>/<img>/<p> 조합으로 콘텐츠 완성
    """
    start_time = time.time()
    request_id = uuid4().hex

    try:
        logger.info(f"[Clova] 콘텐츠 생성 시작 - keyword: {title}")

        # (1) Kakao 이미지 URL은 그대로 사용 (clean_image_url 제거)
        image_urls = [url.strip().strip('"') for url in image_urls]

        # (2) 프롬프트 생성
        prompt = build_prompt(title, article_content)

        headers = {
            "Authorization": f"Bearer {settings.clova_api_key}",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }

        request_body = {
            "messages": [
                {"role": "system", "content": settings.clova_system_prompt},
                {"role": "user", "content": prompt},
            ],
            "topP": 0.8,
            "topK": 0,
            "temperature": 0.7,
            "maxTokens": 3000,
            "repeatPenalty": 5.0,
            "stopBefore": [],
        }

        url = f"https://clovastudio.stream.ntruss.com/v3/tasks/{settings.clova_tuned_model_id}/chat-completions"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=request_body)
            response.raise_for_status()

        result_text = response.json()["result"]["message"]["content"]
        if not result_text.strip():
            raise ValueError("Clova 응답이 비어 있습니다.")

        generated_title = title
        body_text = result_text.strip()

        # (3) HTML 변환 (이미지 포함)
        html_body = convert_to_html_paragraphs(body_text, image_urls)
        final_html = f"<h1>{generated_title}</h1>\n{html_body}"

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "success",
            "title": generated_title,
            "content": final_html,
            "response_time_ms": elapsed_ms,
        }

    except Exception as e:
        logger.error(f"[Clova] 생성 실패 - {e}", exc_info=True)
        return {
            "status": "fail",
            "error_message": str(e),
        }
