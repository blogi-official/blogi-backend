def request_clova_regenerate(keyword_id: int):
    """
    FastAPI 호출 전 임시 테스트용 모킹 함수
    keyword_id를 받아서 임의의 post_id와 상태를 리턴합니다.
    실제 연동 전 기능 테스트에 사용하세요.
    """
    # 임의 post_id 생성 (예: keyword_id + 1000)
    post_id = keyword_id + 1000
    status_str = "success"  # 또는 "pending", "failed" 등 상황에 맞게 변경 가능

    # 실제 호출 전 테스트용 반환값
    return post_id, status_str
