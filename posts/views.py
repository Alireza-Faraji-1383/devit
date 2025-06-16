from rest_framework import generics , permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from core.utils.responses import StandardResponse
from django.db.models import Q
from core.permissions import IsNotAuthenticated
from rest_framework import status

from .serializers import PostPreViewSerializer , PostViewSerializer , PostCreateSerializer
from .models import Post , Tag



class PostsView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer

    def get(self, request):
        posts = Post.objects.all().order_by('-created')
        serializer = self.serializer_class(posts, many=True)
        return StandardResponse.success(message='اطلاعات پست ها با موفقیت ارسال شد.',data=serializer.data,status=status.HTTP_200_OK)
    

class PostView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostViewSerializer
    
    def get(self, request, slug):
        post = get_object_or_404(Post,slug=slug)
        serializer = self.serializer_class(post)
        return StandardResponse.success(message='اطلاعات پست  با موفقیت ارسال شد.',data=serializer.data,status=status.HTTP_200_OK)


class PostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostCreateSerializer
    serializer_show = PostViewSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            post_data = self.serializer_show(post).data
            return StandardResponse.success(message='پست با موفقیت ساخته شد.',data=post_data,status=status.HTTP_201_CREATED)
        
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)