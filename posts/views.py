from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from django.db.models import Q

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
    queryset = Post.objects.filter(status='Published').select_related('user').prefetch_related('tags').all().order_by('-created')

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostPreViewSerializer


class PostDetailView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # queryset = Post.objects.select_related('user').prefetch_related('tags').all()
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        
        base_queryset = Post.objects.select_related('user').prefetch_related('tags')

        if user.is_authenticated:
            return base_queryset.filter(
                Q(status='Published') | Q(user=user)
            ).distinct()
        
        return base_queryset.filter(status='Published')
        

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostViewSerializer


class UserPostsView(StandardResponseMixin, generics.ListAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer

    def get_queryset(self):
        profile_owner = get_object_or_404(User, username__iexact=self.kwargs['user'])
        requesting_user = self.request.user
        base_queryset = Post.objects.filter(user=profile_owner)

        if profile_owner == requesting_user:
            return base_queryset.select_related('user').prefetch_related('tags').order_by('-created')
        return base_queryset.filter(status=Post.STATUS_PUBLISHED).select_related('user').prefetch_related('tags').order_by('-created')