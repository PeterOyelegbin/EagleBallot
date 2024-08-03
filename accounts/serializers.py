from rest_framework import serializers
from .models import UserModel


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UserModel
        fields = ('email', 'voters_id', 'password')

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    voters_id = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(write_only=True)

    class Meta:
        fields = ("voters_id", "otp_code")


class RegenerateTokenSerializer(serializers.Serializer):
    voters_id = serializers.CharField(write_only=True)
    
    class Meta:
        fields = ("voters_id")


class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        fields = ('email', 'password')


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    