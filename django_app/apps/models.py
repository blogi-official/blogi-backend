import random

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None  # type: ignore

    class Provider(models.TextChoices):
        GOOGLE = "google"
        NAVER = "naver"
        KAKAO = "kakao"

    class Role(models.TextChoices):
        USER = "user"
        ADMIN = "admin"

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)  # type: ignore
    email = models.EmailField(unique=True)
    social_id = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100)
    profile_image = models.CharField(max_length=500, null=True, blank=True)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"  # 이메일로 로그인하려면 필수
    REQUIRED_FIELDS = ["username"]  # createsuperuser 시 최소 필드

    class Meta:
        db_table = "user"
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"

    def __str__(self) -> str:
        return self.email

    # username이 없을 때 자동 생성
    def save(self, *args, **kwargs):
        if not self.username:
            base = self.email.split("@")[0]

            self.username = f"{base}_{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)


class UserInterest(models.Model):
    class InterestCategory(models.TextChoices):
        ENTERTAINMENT = "연예"
        ECONOMY = "경제"
        SPORTS = "스포츠"
        FASHION = "패션"
        CAR = "자동차"
        TRAVEL = "여행"
        FOOD = "맛집"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=InterestCategory.choices)

    class Meta:
        db_table = "user_interest"
        unique_together = ("user", "category")
        verbose_name = "사용자 관심사"
        verbose_name_plural = "사용자 관심사 목록"

    def __str__(self) -> str:
        return f"{self.user.nickname} - {self.category}"


class Keyword(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20)
    source_category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_collected = models.BooleanField(default=False)
    collected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "keyword"
        verbose_name = "키워드"
        verbose_name_plural = "키워드 목록"
        unique_together = ("title", "category")

    def __str__(self) -> str:
        return self.title


class Article(models.Model):
    keyword = models.OneToOneField(Keyword, on_delete=models.CASCADE, related_name="article")
    title = models.CharField(max_length=255)
    content = models.TextField()
    origin_link = models.CharField(max_length=1000)

    class Meta:
        db_table = "article"
        verbose_name = "기사"
        verbose_name_plural = "기사 목록"

    def __str__(self) -> str:
        return self.title


class GeneratedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_1_url = models.CharField(max_length=1000, null=True, blank=True)
    image_2_url = models.CharField(max_length=1000, null=True, blank=True)
    image_3_url = models.CharField(max_length=1000, null=True, blank=True)
    copy_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "generated_post"
        verbose_name = "생성된 글"
        verbose_name_plural = "생성된 글 목록"
        constraints = [models.UniqueConstraint(fields=["user", "keyword"], name="unique_post_per_user_keyword")]

    def __str__(self) -> str:
        return self.title


class CopyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(GeneratedPost, on_delete=models.CASCADE)
    copied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "copy_log"
        verbose_name = "복사 기록"
        verbose_name_plural = "복사 기록 목록"

    def __str__(self) -> str:
        return f"{self.user.nickname} - post#{self.post.id}"


class AdminLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=50)
    target_id = models.BigIntegerField()
    action = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_log"
        verbose_name = "관리자 로그"
        verbose_name_plural = "관리자 로그 목록"

    def __str__(self) -> str:
        return f"{self.admin.nickname} - {self.action}"


class Image(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)  # 이미지의 진짜 소유자
    post = models.ForeignKey(GeneratedPost, on_delete=models.SET_NULL, null=True, blank=True)  # 선택적 연결
    image_url = models.CharField(max_length=1000)
    order = models.SmallIntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "image"
        verbose_name = "이미지"
        verbose_name_plural = "이미지 목록"

    def __str__(self) -> str:
        if self.post:
            return f"Post#{self.post.id} - Image {self.order}"
        return f"(미연결) Image {self.order}"


class KeywordClickLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "keyword_click_log"
        verbose_name = "키워드 클릭 기록"
        verbose_name_plural = "키워드 클릭 기록 목록"

    def __str__(self) -> str:
        return f"{self.user.nickname} - {self.keyword.title}"


class ClovaStudioLog(models.Model):
    class ClovaStatus(models.TextChoices):
        SUCCESS = "success", "성공"
        FAIL = "fail", "실패"

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ClovaStatus.choices)
    error_message = models.TextField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clova_studio_log"
        verbose_name = "Clova 처리 기록"
        verbose_name_plural = "Clova 처리 기록 목록"

    def __str__(self) -> str:
        return f"{self.keyword.title} - {self.status}"
