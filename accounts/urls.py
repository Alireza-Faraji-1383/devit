from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import (SearchUserView, TokenRefreshView ,UserRegisterView , UserLoginView , UserLogoutView  , UserInfoView ,  UserChangeView 
                    ,UserSendActivationView , UserActivateView , PasswordResetCodeView , PasswordResetView
                    ,UserFollowView , UserFollowersView , UserFollowingView
)
urlpatterns = [

    path('refresh_from_cookie/', TokenRefreshView.as_view(), name='token_refresh_from_cookie'),
    path('signup/', UserRegisterView.as_view(), name='signup'),
    path('send_activation/', UserSendActivationView.as_view(), name='send_activation'),
    path('activate/<str:uidb64>/<str:token>/', UserActivateView.as_view(), name='activate'),
    path('signin/', UserLoginView.as_view(), name='signin'),
    path('signout/', UserLogoutView.as_view(), name='signout'),
    path('password_reset_code/', PasswordResetCodeView.as_view(), name='password_reset_code'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    
    path('me/', UserChangeView.as_view(), name='user'),
    path("user/<str:username>/followers/", UserFollowersView.as_view(), name="user_followers"),
    path("user/<str:username>/following/", UserFollowingView.as_view(), name="user_following"),
    path('user/<str:username>/follow/', UserFollowView.as_view(), name='user_follow'),
    path('user/<str:username>/', UserInfoView.as_view(), name='user'),
    path('search/<str:search>/', SearchUserView.as_view(), name='search_user'),
    

    

    # JWT
    # path('token/', UserLoginView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]