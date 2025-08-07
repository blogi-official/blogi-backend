# -*- coding: utf-8 -*-

import os

import requests
from dotenv import load_dotenv

# 1. .local.env 로딩
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # fastapi_app/scripts/
ENV_PATH = os.path.join(BASE_DIR, "..", "envs", ".local.env")
load_dotenv(dotenv_path=ENV_PATH)

# 2. 환경변수 로드
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
CLOVA_BASE_URL = os.getenv("CLOVA_BASE_URL")
CLOVA_BUCKET_NAME = os.getenv("CLOVA_BUCKET_NAME")
CLOVA_DATA_PATH = os.getenv("CLOVA_DATA_PATH")
CLOVA_STORAGE_ACCESS_KEY = os.getenv("CLOVA_STORAGE_ACCESS_KEY")
CLOVA_STORAGE_SECRET_KEY = os.getenv("CLOVA_STORAGE_SECRET_KEY")
CLOVA_REQUEST_ID = os.getenv("CLOVA_REQUEST_ID", "blogi-tuning-request-001")

# 3. 필수값 확인
if not all(
    [
        CLOVA_API_KEY,
        CLOVA_BASE_URL,
        CLOVA_BUCKET_NAME,
        CLOVA_DATA_PATH,
        CLOVA_STORAGE_ACCESS_KEY,
        CLOVA_STORAGE_SECRET_KEY,
    ]
):
    print("❌ .env 값이 누락되었습니다. 모든 필드를 확인해주세요.")
    exit(1)


# 4. 튜닝 요청 클래스 정의
class CreateTaskExecutor:
    def __init__(self, host, uri, api_key, request_id):
        self._host = host
        self._uri = uri
        self._api_key = api_key
        self._request_id = request_id

    def _send_request(self, create_request):
        headers = {
            "Authorization": self._api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json",
        }
        result = requests.post(self._host + self._uri, json=create_request, headers=headers).json()
        return result

    def execute(self, create_request):
        res = self._send_request(create_request)
        if "status" in res and res["status"]["code"] == "20000":
            return res["result"]
        else:
            return res


# 5. 실행
if __name__ == "__main__":
    print("🚀 Clova 튜닝 요청 시작...")
    print(f"📂 Dataset: {CLOVA_BUCKET_NAME}/{CLOVA_DATA_PATH}")

    completion_executor = CreateTaskExecutor(
        host=CLOVA_BASE_URL, uri="/tuning/v2/tasks", api_key=f"Bearer {CLOVA_API_KEY}", request_id=CLOVA_REQUEST_ID
    )

    request_data = {
        "name": "blogi_train_v17.csv",
        "model": "HCX-005",
        "tuningType": "PEFT",
        "trainEpochs": "8",  # 문자열 그대로 유지
        "learningRate": "1e-5f",  # ✅ 절대로 바꾸지 않음
        "trainingDatasetBucket": CLOVA_BUCKET_NAME,
        "trainingDatasetFilePath": CLOVA_DATA_PATH,
        "trainingDatasetAccessKey": CLOVA_STORAGE_ACCESS_KEY,
        "trainingDatasetSecretKey": CLOVA_STORAGE_SECRET_KEY,
    }

    response = completion_executor.execute(request_data)

    print("📤 요청 데이터:", request_data)
    print("📥 응답 결과 전체:", response)

    # 👇 응답 분기 처리만 추가 (기존 환경변수는 절대 안 건드림)
    if response.get("status") == "FAILED":
        status_info = response.get("statusInfo", {})
        print("❌ 튜닝 실패")
        print(f"⛔ 실패 사유: {status_info.get('failureReason')}")
        print(f"🪵 상세 메시지: {status_info.get('message')}")
    elif response.get("status") == "WAIT":
        print("⏳ 학습 대기 중 (WAIT)")
        print(f"🆔 Task ID: {response.get('id')}")
    elif response.get("status") == "SUCCEEDED":
        print("✅ 튜닝 성공")
        print(f"🆔 Task ID: {response.get('id')}")
    else:
        print("⚠️ 예상치 못한 응답 상태:", response.get("status"))
