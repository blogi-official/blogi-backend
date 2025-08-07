import os
import requests
from dotenv import load_dotenv

# ✅ 1. .local.env 위치 설정 (fastapi_app/envs/.local.env)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # fastapi_app/scripts/
ENV_PATH = os.path.join(BASE_DIR, "..", "envs", ".local.env")
load_dotenv(dotenv_path=ENV_PATH)

# ✅ 2. 환경 변수 로딩
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
CLOVA_BASE_URL = os.getenv("CLOVA_BASE_URL")
CLOVA_BUCKET_NAME = os.getenv("CLOVA_BUCKET_NAME")
CLOVA_DATA_PATH = os.getenv("CLOVA_DATA_PATH")
CLOVA_STORAGE_ACCESS_KEY = os.getenv("CLOVA_STORAGE_ACCESS_KEY")
CLOVA_STORAGE_SECRET_KEY = os.getenv("CLOVA_STORAGE_SECRET_KEY")

# ✅ 3. 유효성 확인
if not all([CLOVA_API_KEY, CLOVA_BASE_URL, CLOVA_BUCKET_NAME, CLOVA_DATA_PATH, CLOVA_STORAGE_ACCESS_KEY, CLOVA_STORAGE_SECRET_KEY]):
    print("❌ .env 값이 누락되었습니다. 모든 필드를 확인해주세요.")
    exit(1)

# ✅ 4. Clova 튜닝 생성 API 요청
url = f"{CLOVA_BASE_URL}/tuning/v2/tasks"
headers = {
    "Authorization": f"Bearer {CLOVA_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "name": "blogi-tuning-v1",
    "model": "HCX-003",
    "tuningType": "PEFT",
    "trainEpochs": 8,
    "learningRate": "1e-5",
    "trainingDatasetBucket": CLOVA_BUCKET_NAME,
    "trainingDatasetFilePath": CLOVA_DATA_PATH,
    "trainingDatasetAccessKey": CLOVA_STORAGE_ACCESS_KEY,
    "trainingDatasetSecretKey": CLOVA_STORAGE_SECRET_KEY
}

print("🚀 Clova 튜닝 요청 시작...")
print(f"📂 Dataset: {CLOVA_BUCKET_NAME}/{CLOVA_DATA_PATH}")

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    print("✅ 튜닝 생성 성공!")
    print("🆔 튜닝 ID:", result["result"]["id"])
    print("📊 상태:", result["result"]["status"])
    print("📡 응답 전체:")
    print(result)

except requests.HTTPError as e:
    print("❌ 요청 실패:", e)
    print("🔍 응답:", response.text)
