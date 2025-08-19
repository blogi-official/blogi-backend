import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def build_origin_link(item: dict) -> Optional[str]:
    try:
        bloggerlink = item.get("bloggerlink", "")
        if not bloggerlink.startswith("http"):
            bloggerlink = "https://" + bloggerlink

        parsed_blogger = urlparse(bloggerlink)
        blog_id = parsed_blogger.path.strip("/")

        link = item.get("link", "")
        parsed_link = urlparse(link)
        path_parts = parsed_link.path.strip("/").split("/")
        post_id = path_parts[-1] if path_parts else ""

        if not blog_id or not post_id:
            logger.warning(f"[블로그 링크 조합 실패 - 아이디 또는 포스트ID 없음] item={item}")
            return None

        return f"https://blog.naver.com/{blog_id}/{post_id}"
    except Exception as e:
        logger.warning(f"[블로그 링크 조합 실패] item={item}, error={e}")
        return None
