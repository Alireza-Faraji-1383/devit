from rest_framework import generics , permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Follow, User
from .serializers import   FollowSerializer, UserAuthSerializer , UserInfoSerializer , UserRegisterSerializer
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
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "شما با موفقیت ثبت نام کردید"}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserAuthSerializer
    serializer_show = UserInfoSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                response = Response({
                    "message": "شما با موفقیت ورود کردید.",
                    "data": self.serializer_show(user).data
                }, status=status.HTTP_200_OK)

                response.set_cookie("access_token", str(refresh.access_token), httponly=True, samesite='Lax')
                response.set_cookie("refresh_token", str(refresh), httponly=True, samesite='Lax')
                return response
        
            return Response({"error": "نام کاربری یا رمز عبور نادرست است."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    


class UserChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserInfoSerializer

    def get(self,request):
        serializer = self.serializer_class(request.user)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)

    def patch(self,request):
        serializer = self.serializer_class(request.user, data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data})
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)









class UserFollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # serializer_class = FollowSerializer

    def post(self,request, username):
        user = get_object_or_404(User, username=username)
        if request.user == user:
            return Response({"errors": "شما نمی توانید خود را دنبال کنید."}, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get_or_create(follower=request.user , followed=user)
        return Response({"message": "شما با موفقیت دنبال کردید."}, status=status.HTTP_201_CREATED)
    
    def delete(self,request, username):
        user = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user , followed=user).delete()
        return Response({"message": "شما با موفقیت از لیست دنبال کننده ها حذف کردید."}, status=status.HTTP_200_OK)


