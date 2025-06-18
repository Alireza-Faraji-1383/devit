from rest_framework import generics , permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from core.utils.responses import StandardResponse
from django.db.models import Q
from core.permissions import IsNotAuthenticated , IsOwner , IsOwnerOrReadOnly
from rest_framework import status

from accounts.models import User
from .serializers import PostPreViewSerializer , PostViewSerializer , PostCreateUpdateSerializer , MediaSerializer
from .models import Post , Tag , Media



class MediaCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={"request": request})
        if serializer.is_valid():
            media = serializer.save()
            data_show = serializer.data
            data_show['media'] = media.media.url
            return StandardResponse.success(message='مدیا با موفقیت اضافه شد.',data=data_show,status=status.HTTP_201_CREATED)
        return StandardResponse.error(errors=serializer.errors , status=status.HTTP_400_BAD_REQUEST)

# class MediaView(APIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
#     serializer_class = MediaSerializer

#     def get(self , request , slug):
#         media = get_object_or_404(Media,slug=slug)
#         serializer = self.serializer_class(media)
#         data_show = serializer.data
#         data_show['media'] = media.media.url
        
#         return StandardResponse.success(message='اطلاعات مدیا با موفقیت ارسال شد.',data=data_show,status=status.HTTP_200_OK)
    
#     def put(self , request , slug):
#         media = get_object_or_404(Media,slug=slug)
#         self.check_object_permissions(request , media)
#         serializer = self.serializer_class(media, data=request.data,context={"request": request})

#         if serializer.is_valid():
#             serializer.save()
#             data_show = serializer.data
#             data_show['media'] = media.media.url

#             return StandardResponse.success(message='اطلاعات مدیا با موفقیت تفیر یافت.',data=data_show,status=status.HTTP_200_OK)
#         return StandardResponse.error(errors=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    


class PostsView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer
    

    def get(self, request):
        posts = Post.objects.all().order_by('-created')
        serializer = self.serializer_class(posts, many=True)
        return StandardResponse.success(message='اطلاعات پست ها با موفقیت ارسال شد.',data=serializer.data,status=status.HTTP_200_OK)
    

class PostView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    serializer_show = PostViewSerializer
    serializer_class = PostCreateUpdateSerializer
    
    def get(self, request, slug):
        post = get_object_or_404(Post,slug=slug)
        serializer = self.serializer_show(post)
        return StandardResponse.success(message='اطلاعات پست  با موفقیت ارسال شد.',data=serializer.data,status=status.HTTP_200_OK)


    def put(self, request, slug):
        post = get_object_or_404(Post,slug=slug)
        user = request.user
        self.check_object_permissions(request , post)
        serializer = self.serializer_class(post, data=request.data,partial=True,context={"request": request},)
        if serializer.is_valid():
            serializer.save()
            post_data = self.serializer_show(post).data
            return StandardResponse.success(message='پست با موفقیت به روز شد.',data=post_data,status=status.HTTP_200_OK)
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        post = get_object_or_404(Post,slug=slug)
        self.check_object_permissions(request , post)
        post.delete()
        return StandardResponse.success(message='پست با موفقیت حذف شد.',status=status.HTTP_200_OK)




class PostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostCreateUpdateSerializer
    serializer_show = PostViewSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            post_data = self.serializer_show(post).data
            return StandardResponse.success(message='پست با موفقیت ساخته شد.',data=post_data,status=status.HTTP_201_CREATED)
        
        return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserPostsView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer

    def get(self, request , user):
        user = get_object_or_404(User, username = user)
        posts = Post.objects.filter(user=user).order_by('-created')
        serializer = self.serializer_class(posts, many=True)
        return StandardResponse.success(message='اطلاعات پست های کاربر با موفقیت ارسال شد.',data=serializer.data,status=status.HTTP_200_OK)
    

