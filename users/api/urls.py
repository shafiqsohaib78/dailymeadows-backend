# from django.contrib import admin
# from django.conf import settings
# from django.urls import path, include
# from django.conf.urls.static import static
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView, TokenVerifyView
# )
# from .views import MyTokenObtainPairView


# urlpatterns = [
#     path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
# ]

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    LoginAPIView,
    BlacklistRefreshView,
    UserRetrieveUpdateAPIView, RefreshTokenAPIView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login_user'),
    path('logout/', BlacklistRefreshView.as_view(), name="logout_user"),
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshTokenAPIView.as_view(), name='token_refresh_2'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
