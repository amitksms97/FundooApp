import redis
from django.conf import settings
from rest_framework.response import Response
import logging
from rest_framework import generics, status, views, permissions
from rest_framework import status
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import User
from .utils import Util
import jwt
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer, \
    ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)

# Create your views here.
logger = logging.getLogger('django')


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        """
              This api is to register the user to this application
              @param request: username, email and password
              @return: account verification link to registered email once registration is successful
        """
        try:
            user = request.data
            serializer = self.serializer_class(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256') #todo wrapper [1]. create your own token manager class
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify')
            abs_url = 'http://' + current_site + relative_link + "?token=" + str(token)  #todo check schema for http from server side
            email_body = 'Hi ' + user.username + \
                         ' Use the link below to verify your email \n' + abs_url #todo create html body
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Verify your email'}
            Util.send_email(data)
            logger.info("Email Sent Successfully to the user")
            return Response(user_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            return Response({'message': 'Failed to register new user'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    """
        This api is for verification of email to this application
        @param request: once the account verification link is clicked by user this will take that request
        @return: it will return the response of email activation
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
# todo add a if statement to check for token or pass it through the url
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, ['HS256'])
            user = User.objects.get(email=payload['email'])
            if not user.is_active:
                user.is_active = True
                user.save()
            logger.info("Email Successfully Verified")
            return Response({'message': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'message': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response("Something went wrong")

#todo use different level of loggers

class LoginAPIView(generics.GenericAPIView):
    """
            This API is used for authentication of the user
            @param request: user credential like username and password
            @return: it will return the response of successful login
    """
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            token = jwt.encode({'id': user.id}, settings.SECRET_KEY, algorithm='HS256')
            redis_instance.set(user.id, token)
            return Response({'username': user.username, 'token': token}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            logger.error(identifier)
            return Response({'message': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            logger.error(identifier)
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response("Something went wrong")


class RequestPasswordResetEmail(generics.GenericAPIView):
    """
             This api is used to send reset password request to the user
             @param request: user registered email id
             @return: sends a password reset link to user's validated email id
    """
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relative_link = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            redirect_url = request.data.get('redirect_url', '')
            abs_url = 'http://' + current_site + relative_link
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         abs_url + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your password'}
            Util.send_email(data)
        return Response({'message': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):

    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'message': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(views.APIView):

    def post(self, request):

        token = request.META.get("HTTP_TOKEN")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, ['HS256'])
            print(payload)
            user = User.objects.get(id=payload['id'])
            value = redis_instance.get(user.id)
            if not value:
                return Response("Failed to logout", status=status.HTTP_400_BAD_REQUEST)
            else:
                result = redis_instance.delete(user.id)
                if result == 1:
                    return Response("Successully logged out", status=status.HTTP_200_OK)
                else:
                    return Response("Failed to logout please re login", status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError as identifier:
            logger.error(identifier)
            return Response({'message': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            logger.error(identifier)
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Something went wrong please try again'})


#todo
'''''
Exception handling in code
Include specific exceptions
Methods not commented 
Standard keys for response throughout the applications
usage of different log levels have to be done
create custom decorators 
crud operation 
concept of soft delete should be implemented
date and time stamp should be maintained
'''''
#todo use a single key
#gitignore file should be added
#remove .idea file from git repisotry