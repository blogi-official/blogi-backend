# apps/users/serializers/profile_serializers.py

import random

from rest_framework import serializers

from apps.models import User, UserInterest


# 닉네임, 카테고리 설정
class UserInterestSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=20, required=False)
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=UserInterest.InterestCategory.choices), allow_empty=False
    )

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("해당 닉네임은 이미 사용 중입니다.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        nickname = validated_data.get("nickname")

        # 닉네임 없을 경우 랜덤 생성
        if not nickname:
            while True:
                nickname = f"블로기유저-{random.randint(1000, 9999)}"
                if not User.objects.filter(nickname=nickname).exists():
                    break
        else:
            user.nickname = nickname

        user.nickname = nickname
        user.save()

        # 기존 관심사 삭제 후 재등록
        UserInterest.objects.filter(user=user).delete()
        categories = validated_data["categories"]
        for category in categories:
            UserInterest.objects.create(user=user, category=category)

        return {"id": user.id, "nickname": user.nickname, "categories": categories}


# 프로필 조회


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "nickname", "provider", "created_at")


# 닉네임 및 관심사 수정
from rest_framework import serializers

from apps.models import User, UserInterest


class UserUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=20)
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=UserInterest.InterestCategory.choices),
        allow_empty=False,
        error_messages={"empty": "관심사는 최소 1개 이상 선택해야 합니다."},
    )

    def validate_nickname(self, value):
        user = self.context["request"].user
        if User.objects.exclude(id=user.id).filter(nickname=value).exists():
            raise serializers.ValidationError("해당 닉네임은 이미 사용 중입니다.")
        return value

    def update(self, instance, validated_data):
        nickname = validated_data.get("nickname")
        categories = validated_data.get("categories")

        # 닉네임 수정
        instance.nickname = nickname
        instance.save()

        # 기존 관심사 삭제
        UserInterest.objects.filter(user=instance).delete()

        # 새 관심사 등록
        interests = [UserInterest(user=instance, category=category) for category in categories]
        UserInterest.objects.bulk_create(interests)

        return instance

    def to_representation(self, instance):
        categories = UserInterest.objects.filter(user=instance).values_list("category", flat=True)
        return {
            "message": "사용자 정보 수정 완료",
            "user_info": {
                "id": instance.id,
                "nickname": instance.nickname,
                "categories": list(categories),
            },
        }
