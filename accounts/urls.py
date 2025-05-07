from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import UserRegisterView , UserLoginView , test , TokenRefreshView , UserLogoutView

urlpatterns = [

    path('refresh_from_cookie/', TokenRefreshView.as_view(), name='token_refresh_from_cookie'),
    path('register/', UserRegisterView.as_view(), name='user'),
    path('login/', UserLoginView.as_view(), name='logout'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    path('test/', test.as_view(), name='test'),
    

    # JWT
    # path('token/', UserLoginView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]