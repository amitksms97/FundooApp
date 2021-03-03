from rest_framework import serializers
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate
import re

email_pattern = "^[a-zA-z]{3}[0-9a-zA-Z\\.\\_\\-\\+]*@[a-z]*\\.(co|com.au|in|net|in|com.com|com|)$"
password = "^(?=.*[0-9])" + "(?=.*[a-z])(?=.*[A-Z])" + "(?=.*[@#$%^&+=]).{8,20}"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'
    }

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not re.match(email, email):
            raise serializers.ValidationError(self.default_error_messages)
        if not username.isalnum():
            raise serializers.ValidationError("Invalid Email")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'username']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)

        try:
            if not user:
                raise AuthenticationFailed('Invalid credentials, try again')
            if not user.is_active:
                raise AuthenticationFailed('Account disabled, contact admin')
            if not user.is_verified:
                raise AuthenticationFailed('EMAIL ID IS NOT VERIFIED YET')
        except serializers.ValidationError as identifier:
            return {'error': "check with your email and password"}

        return {
            'email': user.email,
            'username': user.username
            }
        #return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email', '')
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                raise serializers.ValidationError("This email id is not verified!!")
        except User.DoesNotExist:
            raise serializers.ValidationError("This email is not registerd")

        return attrs


class SetNewPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)
    new_password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64', 'new_password']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            new_password = attrs.get('NewPassword', '')
            if password != new_password:
                raise serializers.ValidationError("Password not matched!!")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(new_password)
            user.save()
            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
