from rest_framework import generics , permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import   UserAuthSerializer
from rest_framework_simplejwt.tokens import RefreshToken , TokenError
from rest_framework import status


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
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username,password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response({"message": "شما با موفقیت وارد شدید."}, status=status.HTTP_200_OK)

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


class test(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        return Response({"message": "Hello"})
