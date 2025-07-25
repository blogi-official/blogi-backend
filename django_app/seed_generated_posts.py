import random

from django.utils import timezone

from apps.models import GeneratedPost, Keyword, User

# 014 용 더비 DB
user = User.objects.get(id=9)

for i in range(5):
    title = f"테스트 키워드 {i+11}"

    keyword, created = Keyword.objects.get_or_create(
        title=title,
        defaults={"category": "연예", "is_active": True, "is_collected": True, "collected_at": timezone.now()},
    )

    content = """
    <h2>2025년, 인공지능이 바꾸는 우리의 삶</h2>

    <p>
    2025년 현재, 인공지능(AI)은 더 이상 미래의 기술이 아닌, 우리의 일상 속 깊숙이 자리 잡은 현실입니다.  
    콘텐츠 생성, 고객 상담, 교육, 헬스케어 등 다양한 분야에서 AI가 중요한 역할을 하고 있으며, 기술 발전 속도는 그 어느 때보다 빠릅니다.
    </p>

    <img src="https://source.unsplash.com/800x400/?ai,technology" alt="AI 기술 이미지" style="margin: 20px 0; width: 100%; border-radius: 12px;">

    <h3>AI 콘텐츠 생성의 새로운 시대</h3>

    <p>
    블로그, 뉴스, 마케팅 카피 등 텍스트 기반 콘텐츠를 작성하는 데 있어 AI는 이제 핵심 도구가 되었습니다.  
    특히 HyperCLOVA X와 같은 대규모 언어 모델은 사람처럼 자연스러운 문장을 생성할 수 있으며, 다양한 스타일과 톤도 자유자재로 조절 가능합니다.
    </p>

    <p>
    예를 들어, 뉴스 기사를 블로그 스타일로 바꾸거나, 짧은 소셜 콘텐츠를 긴 글로 확장하는 작업이 이전보다 훨씬 수월해졌습니다.
    </p>

    <img src="https://source.unsplash.com/800x400/?writing,blog" alt="AI 콘텐츠 생성 예시" style="margin: 20px 0; width: 100%; border-radius: 12px;">

    <h3>AI와 함께 성장하는 산업들</h3>

    <p>
    교육 분야에서는 AI 튜터가 학생 개개인의 학습 스타일에 맞춘 맞춤형 피드백을 제공하고 있고, 헬스케어에서는 질병 진단부터 치료 추천까지 폭넓은 활용이 이뤄지고 있습니다.
    </p>

    <p>
    또한 자율주행, 음성 비서, 고객 상담 챗봇 등 다양한 서비스가 이미 상용화되어 있으며, 소비자들은 AI의 존재를 '당연한 기술'로 인식하고 있습니다.
    </p>

    <img src="https://source.unsplash.com/800x400/?future,ai" alt="AI와 산업 변화" style="margin: 20px 0; width: 100%; border-radius: 12px;">

    <h3>마무리: AI는 선택이 아닌 필수</h3>

    <p>
    AI 기술은 이제 선택이 아닌 필수입니다.  
    변화의 물결 속에서 우리는 어떻게 활용할지 고민해야 하며, 단순히 기술을 받아들이는 것이 아니라, 이를 통해 어떤 가치를 창출할 수 있을지를 고민해야 합니다.
    </p>

    <p>
    AI가 만들어가는 내일, 이제는 그 중심에 우리가 함께 서야 할 때입니다.
    </p>

    <p><strong>#인공지능 #2025트렌드 #AI콘텐츠 #HyperCLOVA #블로그자동작성</strong></p>
    """

    GeneratedPost.objects.create(
        user=user,
        keyword=keyword,
        title=f"테스트 생성글 제목 {i+1}",
        content=content.strip(),
        image_1_url="https://via.placeholder.com/600x400.png?text=Test+Image+1",
        image_2_url="https://via.placeholder.com/600x400.png?text=Test+Image+2",
        image_3_url="https://via.placeholder.com/600x400.png?text=Test+Image+3",
        copy_count=random.randint(0, 10),
        is_active=True,
        created_at=timezone.now(),
    )
