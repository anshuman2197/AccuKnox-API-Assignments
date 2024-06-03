from rest_framework import serializers
from .models import CustomUser,FriendRequest
from django.core.validators import validate_email

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password'] 
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        value = value.lower()
        validate_email(value) 
        if '@' not in value:
            raise serializers.ValidationError("Email must contain '@'.")
        return value

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data.get('username')
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email).lower()
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  
        instance.save()
        return instance



class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'timestamp']