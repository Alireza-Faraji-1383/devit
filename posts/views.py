from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404

from core.mixins import StandardResponseMixin # Mixin جدید
from core.permissions import IsOwnerOrReadOnly
from accounts.models import User

from .models import Post, Media
from .serializers import (
    PostPreViewSerializer,
    PostViewSerializer,
    PostCreateUpdateSerializer,
    MediaSerializer
)


class MediaCreateView(StandardResponseMixin, generics.CreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaSerializer


class PostListCreateView(StandardResponseMixin, generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.select_related('user').prefetch_related('tags').all().order_by('-created')

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostPreViewSerializer


class PostDetailView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Post.objects.select_related('user').prefetch_related('tags').all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostViewSerializer


class UserPostsView(StandardResponseMixin, generics.ListAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer

    def get_queryset(self):
        user_username = self.kwargs['user']
        user_obj = get_object_or_404(User, username__iexact=user_username)
        
        return Post.objects.filter(user=user_obj).select_related('user').prefetch_related('tags').order_by('-created')