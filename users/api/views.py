# from rest_framework_simplejwt.views import TokenObtainPairView
# from .serializers import MyTokenObtainPairSerializer


# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer


# class PasswordTokenCheckAPI(generics.GenericAPIView):
#     # authentication_classes = ()
#     permission_classes = [permissions.AllowAny]

#     def get(self, request, uidb64, token):

#         try:
#             id = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=id)

#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({'error': 'Token is not valid, please request a new one.', 'status': status.HTTP_401_UNAUTHORIZED})

#             return Response({'success': True, 'message': 'Credentials Valid', 'uibd64': uidb64, 'token': token})

#         except DjangoUnicodeDecodeError as identifier:
#             if not PasswordResetTokenGenerator().check_token(user):
#                 return Response({'error': 'Token is not valid, please request a new one.', 'status': status.HTTP_401_UNAUTHORIZED})
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
)
from .renderers import UserJSONRenderer
from users.models import NewUser as User
from typing import Any, Optional
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta
expire = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]


# class LoginAPIView(APIView):
#     permission_classes = []
#     renderer_classes = (UserJSONRenderer,)
#     serializer_class = LoginSerializer

#     def post(self, request):
#         """Return user after login."""
#         print(request)
#         user = request.data.get('user', {})

#         serializer = self.serializer_class(data=user)
#         if not serializer.is_valid():
#             print(serializer.errors)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         return Response(serializer.data, status=status.HTTP_200_OK)

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data
        email = user['email']
        password = user['password']
        print(email)
        print(password)
        if user.get("email") is None or "":
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.get("password") is None or "":
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user2 = authenticate(username=user.get("email"),
                                 password=user.get("password"))
            print("user", user2)
            if user2 is not None:
                data = {
                    'token': user2.token,
                    'user': user2.id,
                    'u_id': user2.unique_id,
                    'email': user2.email,
                    'is_active': user2.is_active,
                    'is_staff': user2.is_staff,
                    'expire': timezone.now()+expire-timedelta(seconds=200)
                }
                print(data)
                return Response(data, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect Password or Email!'}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        token = request.data
        # token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4NTEyNjI0NywiaWF0IjoxNjg0NTIxNDQ3LCJqdGkiOiJjODM0MjMzNjY5NTI0ZTE4YWZiM2RlNmVlNGE5NGQxZCIsInVzZXJfaWQiOjF9.-m3RZ_ySeJdTkP4NIMCn_eZZH0Td6lvwE1AnOJVv0cs'
        print(token['token'])
        try:
            refresh = RefreshToken(token['token'])
            print(refresh['id'])
            user = User.objects.get(id=refresh["id"])
            if user is not None:

                data = {
                    'token': user.token,
                    'user': user.id,
                    'u_id': user.unique_id,
                    'name': user.name,
                    'username': user.username,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'expire': timezone.now()+expire-timedelta(seconds=200)
                }
                # print(data)
                return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request: Request, *args: dict[str, Any], **kwargs: dict[str, Any]) -> Response:
        """Return user on GET request."""
        serializer = self.serializer_class(
            request.user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, *args: dict[str, Any], **kwargs: dict[str, Any]) -> Response:
        """Return updated user."""
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class BlacklistRefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Success")
