from rest_framework import generics , permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Follow, User
from .serializers import   FollowSerializer, UserAuthSerializer , UserInfoSerializer
from rest_framework_simplejwt.tokens import RefreshToken , TokenError
from rest_framework import status
from django.shortcuts import get_object_or_404


class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({'access_token': access_token}, status=status.HTTP_200_OK)
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
            return response
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        



class UserRegisterView(APIView):
    serializer_class = UserAuthSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response({"message": "شما با موفقیت ثبت نام کردید"}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserInfoSerializer

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username,password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response(self.serializer_class(user).data, status=status.HTTP_200_OK)

            response.set_cookie("access_token", str(refresh.access_token), httponly=True, samesite='Lax')
            response.set_cookie("refresh_token", str(refresh), httponly=True, samesite='Lax')
            return response
        return Response({"error": " نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_401_UNAUTHORIZED)
    

class UserLogoutView(APIView):
    def post(self,request):
        response = Response({"message": "شما با موفقیت خارج شدید."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response




class UserInfoView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserInfoSerializer
    
    def get(self,request , username):
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(user)
        return Response(serializer.data)
    


class UserChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserInfoSerializer

    def get(self,request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self,request):
        serializer = self.serializer_class(request.user, data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)









class UserFollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer

    def post(self,request, username):
        user = get_object_or_404(User, username=username)
        
        if request.user == user:
            return Response({"message": "شما نمی توانید خود را دنبال کنید."}, status=status.HTTP_400_BAD_REQUEST)
        
        follow , created = Follow.objects.get_or_create(follower=request.user , followed=user)
        if not created:
            follow.delete()
            return Response({"message": "فرد مورد نظر از لیست دنبال کننده ها حذف شد"}, status=status.HTTP_200_OK)
        
        return Response({"message": "شما با موفقیت دنبال کردید."}, status=status.HTTP_201_CREATED)


