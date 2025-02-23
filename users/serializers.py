from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'role', 'street', 'city',
            'state', 'country', 'zip_code', 'image', 'phone_number',
            'created_at', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'street': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
            'country': {'required': False},
            'zip_code': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials provided.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials provided.")
        data["user"] = user
        return data
