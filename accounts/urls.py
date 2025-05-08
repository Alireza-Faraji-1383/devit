from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import (TokenRefreshView ,UserRegisterView , UserLoginView , UserLogoutView  , UserInfoView ,  UserChangeView 
                    ,UserFollowView
)
urlpatterns = [

    path('refresh_from_cookie/', TokenRefreshView.as_view(), name='token_refresh_from_cookie'),
    path('register/', UserRegisterView.as_view(), name='user'),
    path('login/', UserLoginView.as_view(), name='logout'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    path('me/', UserChangeView.as_view(), name='user'),
    path('user/<str:username>/', UserInfoView.as_view(), name='user'),
    path('user/<str:username>/follow/', UserFollowView.as_view(), name='user_follow'),
    

    

    # JWT
    # path('token/', UserLoginView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]