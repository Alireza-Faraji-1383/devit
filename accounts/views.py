from rest_framework import generics , permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Follow, User , PasswordResetCode
from .serializers import   (FollowSerializer, PasswordResetCodeSerializer, UserAuthSerializer , UserInfoSerializer , UserRegisterSerializer,
                            UserPreViewSerializer , PasswordResetSerializer)
from rest_framework_simplejwt.tokens import RefreshToken , TokenError
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from core.utils.responses import StandardResponse
from .utils import send_activation_email, send_reset_code
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from core.permissions import IsNotAuthenticated
from django.db.models import Q
from django.db.models import Prefetch




class TokenRefreshView(APIView):
    authentication_classes = []
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            response = Response({'errors': 'هیچ توکنی پیدا نشد. '}, status=status.HTTP_401_UNAUTHORIZED)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({'message': 'توکن با موفقیت انجام شد.'}, status=status.HTTP_200_OK)
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
            return response

        except TokenError:
            response = Response({'errors': 'توکن منقضی یا نامعتبر است.'}, status=status.HTTP_401_UNAUTHORIZED)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        

class UserRegisterView(APIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (IsNotAuthenticated,)

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            user.is_active = False
            user.save()
            send_activation_email(user)
            return StandardResponse.success(message="لطفا ایمیل خود را برسی کنید تا حساب کاربری فعال شود.", status=status.HTTP_201_CREATED)
        return StandardResponse.error(errors= serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserSendActivationView(APIView):
    serializer_class = UserAuthSerializer
    permission_classes = (IsNotAuthenticated,)
    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                return StandardResponse.error(errors="نام کاربری یا رمز عبور نادرست است.", status=status.HTTP_400_BAD_REQUEST)
            if user.is_active:
                return StandardResponse.error(errors="این کاربر قبلا فعال شده است.", status=status.HTTP_400_BAD_REQUEST)

            send_activation_email(user)
            return StandardResponse.success(message="ایمیل با موفقیت ارسال شد.", status=status.HTTP_201_CREATED)
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserActivateView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user == None:
            return StandardResponse.error(errors="کاربر مورد نظر شما وجود ندارد.", status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return StandardResponse.error(errors="حساب کاربری شما قبلا فعال شده است.", status=status.HTTP_400_BAD_REQUEST)

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return StandardResponse.success(message="حساب کاربری شما با موفقیت تایید شد.", status=status.HTTP_200_OK)
        
        return StandardResponse.error(errors="توکن شما خراب یا منقضی شده است.",status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = UserAuthSerializer
    serializer_show = UserInfoSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user:

                if not user.is_active:
                    return StandardResponse.error(errors="حساب کاربری فعال نشده است.", status=status.HTTP_409_CONFLICT)

                refresh = RefreshToken.for_user(user)
                response = Response({
                    "message": "شما با موفقیت ورود کردید.",
                    "data": self.serializer_show(user , context={"request": request}).data
                }, status=status.HTTP_200_OK)

                response.set_cookie("access_token", str(refresh.access_token), httponly=True, samesite='Lax')
                response.set_cookie("refresh_token", str(refresh), httponly=True, samesite='Lax')
                return response
        
            return StandardResponse.error(errors="نام کاربری یا رمز عبور نادرست است.", status=status.HTTP_400_BAD_REQUEST)
        
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogoutView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        response = Response({"message": "شما با موفقیت خارج شدید."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    

class PasswordResetCodeView(APIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = PasswordResetCodeSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = get_object_or_404(User, email=email)
            latest_code = PasswordResetCode.objects.filter(user=user , is_used=False).order_by('-created').first()
            if latest_code and not latest_code.is_expired():
                return StandardResponse.error(errors="لطفا صبر کنید کد قبلی هنوز قابل استفاده است.", status=status.HTTP_429_TOO_MANY_REQUESTS)
            send_reset_code(user)
            return StandardResponse.success(message="کد بازیابی رمز عبور به ایمیل شما ارسال شد.", status=status.HTTP_201_CREATED)
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
class PasswordResetView(APIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = PasswordResetSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = get_object_or_404(User, email=email)
            code = serializer.validated_data.get('code')
            try:
                latest_code = PasswordResetCode.objects.get(user=user , code=code , is_used=False)
            except PasswordResetCode.DoesNotExist:
                return StandardResponse.error(errors="کد اشتباه است", status=status.HTTP_400_BAD_REQUEST)

            if latest_code.is_expired():
                return StandardResponse.error(errors="کد بازیابی شما منقضی شده است.", status=status.HTTP_400_BAD_REQUEST)
            
            latest_code.is_used = True
            latest_code.save()
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return StandardResponse.success(message="شما با موفقیت رمز عبور خود را تغییر کردید.", status=status.HTTP_200_OK)
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserInfoSerializer
    
    def get(self,request , username):
        user = get_object_or_404(User, username__iexact=username)
        serializer = self.serializer_class(user, context={"request": request})
        return StandardResponse.success(data=serializer.data,status=status.HTTP_200_OK)
    

class UserChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserInfoSerializer

    def get(self,request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return StandardResponse.success(message="اطلاعات گرفته شد.", data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        if not request.data:
            return StandardResponse.error(errors="حداثل یک فیلد خود را برای تغیر ارسال کنید.", status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(request.user, data=request.data , partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return StandardResponse.success(message="شما با موفقیت اطلاعات خود بروز کردید.", data=serializer.data, status=status.HTTP_200_OK)
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SearchUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserPreViewSerializer
    def get(self,request , search):
        query = search
        users = User.objects.filter(Q(username__icontains=query))
        serializer = self.serializer_class(users, many=True, context={'request': request})
        return StandardResponse.success(message="اطلاعات جستجو شد.", data=serializer.data, status=status.HTTP_200_OK)



class UserFollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # serializer_class = FollowSerializer

    def post(self,request, username):
        user = get_object_or_404(User, username=username)
        if request.user == user:
            return StandardResponse.error(errors="شما نمی توانید خود را دنبال کنید.", status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get_or_create(follower=request.user , followed=user)
        return StandardResponse.success(message="شما با موفقیت دنبال کردید.", status=status.HTTP_201_CREATED)
    
    def delete(self,request, username):
        user = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user , followed=user).delete()
        return StandardResponse.success(message="شما با موفقیت از لیست دنبال کننده ها حذف کردید.", status=status.HTTP_200_OK)
    


class UserFollowersView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserPreViewSerializer
    def get(self,request, username):
        user = get_object_or_404(User,username=username)
        queryset = User.objects.filter(
            following__followed=user
        ).exclude(pk=user.pk).distinct().prefetch_related(
            Prefetch(
                'following',
                queryset=Follow.objects.filter(followed=user),
                to_attr='my_followers'
            )
        )
        serializer = UserPreViewSerializer(queryset, many=True, context={'request': request})
        return StandardResponse.success(message="اطلاعات جستجو شد.", data=serializer.data, status=status.HTTP_200_OK)
    

class UserFollowingView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserPreViewSerializer
    def get(self,request, username):
        user = get_object_or_404(User,username=username)
        queryset = User.objects.filter(
            followers__follower=user
        ).exclude(pk=user.pk).distinct().prefetch_related(
            Prefetch(
                'followers',
                queryset=Follow.objects.filter(follower=user),
                to_attr='my_following'
            )
        )
        serializer = UserPreViewSerializer(queryset, many=True, context={'request': request})
        return StandardResponse.success(message="اطلاعات جستجو شد.", data=serializer.data, status=status.HTTP_200_OK)
        


