from django.db import models


class User(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google"
        NAVER = "naver"
        KAKAO = "kakao"

    class Role(models.TextChoices):
        USER = "user"
        ADMIN = "admin"

    email = models.CharField(max_length=255, unique=True)
    social_id = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100)
    profile_image = models.CharField(max_length=500, null=True, blank=True)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user"

    def __str__(self) -> str:
        return self.email


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

    def __str__(self) -> str:
        return f"{self.user.nickname} - {self.category}"


class Keyword(models.Model):
    title = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=20)
    source_category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_collected = models.BooleanField(default=False)
    collected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "keyword"

    def __str__(self) -> str:
        return self.title


class Article(models.Model):
    keyword = models.OneToOneField(Keyword, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    origin_link = models.CharField(max_length=1000)

    class Meta:
        db_table = "article"

    def __str__(self) -> str:
        return self.title


class GeneratedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.OneToOneField(Keyword, on_delete=models.CASCADE)
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

    def __str__(self) -> str:
        return self.title


class CopyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(GeneratedPost, on_delete=models.CASCADE)
    copied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "copy_log"

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

    def __str__(self) -> str:
        return f"{self.admin.nickname} - {self.action}"


class Image(models.Model):
    post = models.ForeignKey(GeneratedPost, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=1000)
    order = models.SmallIntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "image"

    def __str__(self) -> str:
        return f"Post#{self.post.id} - Image {self.order}"


class KeywordClickLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "keyword_click_log"

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

    def __str__(self) -> str:
        return f"{self.keyword.title} - {self.status}"
