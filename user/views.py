from django.conf import settings
from rest_framework.response import Response
import logging
from rest_framework import generics, status, views, permissions
from rest_framework import status
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.schemas import openapi

from .models import User
from .utils import Util
import jwt
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer, \
    ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, LogoutSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import login, logout
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


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
            token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify')
            abs_url = 'http://' + current_site + relative_link + "?token=" + str(token)
            email_body = 'Hi ' + user.username + \
                         ' Use the link below to verify your email \n' + abs_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Verify your email'}
            Util.send_email(data)
            logger.info("Email Sent Successfully to the user")
            return Response(user_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'Failed to register new user'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    """
        This api is for verification of email to this application
        @param request: once the account verification link is clicked by user this will take that request
        @return: it will return the response of email activation
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, ['HS256'])
            user = User.objects.get(email=payload['email'])
            if not user.is_active:
                user.is_active = True
                user.save()
            logger.info("Email Successfully Verified")
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        #todo add generic


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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

#todo use both generic and specific ecxeption 2. Use comments and docstring

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    """
           This api is to log out the user
           @return: release all resources from user on logging out
    """
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(e)
            return Response({'details': 'something went wrong while logout'}, status=status.HTTP_403_FORBIDDEN)

'''''
class LogoutAPIView(generics.GenericAPIView):
    """
           This api is to log out the user
           @return: release all resources from user on logging out
    """
    serializer_class = LoginSerializer

    def get(self, request):
        try:
            user = request.user
            logout(request)
            logger.info('You have been successfully logged out, Thank You!!')
            return Response({'details': 'You have been successfully logged out, Thank You!!'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details': 'something went wrong while logout'}, status=status.HTTP_403_FORBIDDEN)
'''''