from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import (TokenRefreshView ,UserRegisterView , UserLoginView , UserLogoutView  , UserInfoView ,  UserChangeView 
                    ,UserSendActivationView , UserActivateView
                    ,UserFollowView 
)
urlpatterns = [

    path('refresh_from_cookie/', TokenRefreshView.as_view(), name='token_refresh_from_cookie'),
    path('signup/', UserRegisterView.as_view(), name='signup'),
    path('send_activation/', UserSendActivationView.as_view(), name='send_activation'),
    path('activate/<str:uidb64>/<str:token>/', UserActivateView.as_view(), name='activate'),
    path('signin/', UserLoginView.as_view(), name='signin'),
    path('signout/', UserLogoutView.as_view(), name='signout'),
    
    path('me/', UserChangeView.as_view(), name='user'),
    path('user/<str:username>/', UserInfoView.as_view(), name='user'),
    path('user/<str:username>/follow/', UserFollowView.as_view(), name='user_follow'),
    

    

    # JWT
    # path('token/', UserLoginView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]