from django.test import TestCase
from rest_framework.test import APIClient


class KeywordCreateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_mock_keyword_create(self):
        mock_payload = [
            {
                "title": "테스트1",
                "category": "연예",
                "source_category": "엔터 종합",
                "collected_at": "2025-07-25T00:00:00Z",
            },
            {
                "title": "테스트2",
                "category": "경제",
                "source_category": "경제 종합",
                "collected_at": "2025-07-25T00:00:00Z",
            },
        ]
        response = self.client.post("/api/internal/posts/", mock_payload, format="json")
        self.assertEqual(response.status_code, 201, msg=f"응답 본문: {response.content}")
        print(response.json())
