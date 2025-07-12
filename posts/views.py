from django.db import IntegrityError
from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Count, Exists, OuterRef , Prefetch
from rest_framework.views import APIView
from django.db import models


from core.mixins import StandardResponseMixin # Mixin جدید
from core.permissions import IsOwnerOrReadOnly
from accounts.models import User
from core.utils.responses import StandardResponse
from rest_framework import filters

from .models import Post, Media , LikePost , Comment, Tag , VoteComment , SavedPost , PostView
from .serializers import (
    PostPreViewSerializer,
    PostViewSerializer,
    PostCreateUpdateSerializer,
    MediaSerializer,
    CommentSerializer,
    ReplySerializer,
    CommentCreateUpdateSerializer,
    TagListSerializer
)


class MediaCreateView(StandardResponseMixin, generics.CreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaSerializer


class PostListCreateView(StandardResponseMixin, generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content','slug', 'tags__title']
    ordering_fields = ['created', 'likes_count','updated']
    ordering = ['-created']

    def get_queryset(self):
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED).with_likes(self.request.user).with_saved_status(self.request.user).with_view_count().with_comments_count().select_related('user').prefetch_related('tags')
        
    def get_serializer_class(self):

        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostPreViewSerializer


class PostDetailView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # queryset = Post.objects.select_related('user').prefetch_related('tags').all()
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.visible_to(
            self.request.user).with_likes(self.request.user).with_saved_status(self.request.user).with_view_count().with_comments_count().select_related('user').prefetch_related('tags')
    
    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        if request.user.is_authenticated:
            PostView.objects.get_or_create(user=request.user, post=instance)
            
        serializer = self.get_serializer(instance)
        return StandardResponse.success(message='پست با موفقیت بازیابی شد', data=serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostViewSerializer


class UserPostsView(StandardResponseMixin, generics.ListAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = PostPreViewSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content','slug', 'tags__title']
    ordering_fields = ['created', 'likes_count','updated','status']
    ordering = ['-created']

    def get_queryset(self):
        profile_owner = get_object_or_404(User, username__iexact=self.kwargs['user'])
        
        base_queryset = Post.objects.filter(user=profile_owner)
        if profile_owner != self.request.user:
            base_queryset = base_queryset.filter(status=Post.STATUS_PUBLISHED)
        
        return base_queryset.with_likes(self.request.user).with_saved_status(self.request.user).with_view_count().with_comments_count().select_related('user').prefetch_related('tags').order_by('-created')
    


class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        user = request.user
        try:
            like = LikePost.objects.create(user=user, post=post)
            return StandardResponse.success(message='شما پست را لایک کردید',status=status.HTTP_200_OK)
        except IntegrityError:
            return StandardResponse.error(message='',errors='شما قبلا این پست را لایک کردید',status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request, slug):
        post = get_object_or_404(Post, slug=slug)
        user = request.user
        deleted_count, _ = LikePost.objects.filter(user=user, post=post).delete()
        if deleted_count > 0:
            return StandardResponse.success(message='شما لایک پست را حذف کردید',status=status.HTTP_200_OK)
        else:
            return StandardResponse.error(message='شما این پست را لایک نکرده بودید.', status=status.HTTP_404_NOT_FOUND)
        

class PostSaveToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        _, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        if not created:
            return StandardResponse.error(message="این پست قبلاً ذخیره شده است.", status=status.HTTP_409_CONFLICT)
        return StandardResponse.success(message="پست با موفقیت ذخیره شد.", status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        deleted_count, _ = SavedPost.objects.filter(user=request.user, post=post).delete()
        if deleted_count == 0:
            return StandardResponse.error(message="این پست در لیست شما وجود نداشت.", status=status.HTTP_404_NOT_FOUND)
        return StandardResponse.success(message="پست با موفقیت حذف شد.", status=status.HTTP_200_OK)

class SavedPostListView(StandardResponseMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostPreViewSerializer

    def get_queryset(self):
        return Post.objects.filter(
            saved_by__user=self.request.user
        ).with_likes(self.request.user).with_saved_status(self.request.user).with_view_count().select_related('user').prefetch_related('tags').order_by('-saved_by__created').distinct()


class CommentListCreateView(StandardResponseMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs.get('slug')
        post = get_object_or_404(Post, slug=post_slug)
        user = self.request.user

        replies_queryset = Comment.objects.with_votes(
            user
        ).select_related(
            'user'
        ).prefetch_related(
            'replies'
        )
        prefetch_replies = Prefetch('replies', queryset=replies_queryset)

        return Comment.objects.filter(
            post=post,
            parent__isnull=True
        ).with_votes(
            user
        ).select_related(
            'user'
        ).prefetch_related(
            prefetch_replies
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateUpdateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post_slug = self.kwargs.get('slug')
        post = get_object_or_404(Post, slug=post_slug)
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.with_votes(self.request.user).select_related('user').prefetch_related('replies__user')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CommentCreateUpdateSerializer
        return CommentSerializer


class CommentVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        vote_type = request.data.get('vote_type')

        if vote_type not in [VoteComment.LIKE, VoteComment.DISLIKE]:
            return StandardResponse.error("مقدار رای نامعتبر است.", status=status.HTTP_400_BAD_REQUEST)

        vote, created = VoteComment.objects.update_or_create(
            user=request.user, comment=comment,
            defaults={'vote': vote_type}
        )
        return StandardResponse.success(message="رای شما ثبت شد.", status=status.HTTP_200_OK)

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        VoteComment.objects.filter(user=request.user, comment=comment).delete()
        return StandardResponse.success(message="رای شما حذف شد.", status=status.HTTP_200_OK)
    

class CommentRepliesListView(StandardResponseMixin, generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer 

    def get_queryset(self):
        parent_comment_id = self.kwargs.get('pk')
        parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
        
        return Comment.objects.filter(
            parent=parent_comment
        ).with_votes(
            self.request.user
        ).select_related('user').prefetch_related('replies__user')
    

class TagListView(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagListSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title','posts_count']

    ordering = ['-posts_count'] 

    def get_queryset(self):

        published_posts_count = Count('posts',filter=Q(posts__status=Post.STATUS_PUBLISHED))
        return Tag.objects.annotate(
            posts_count=published_posts_count
        ).filter(posts_count__gt=0 )
        
    
class PostTagListView(StandardResponseMixin, generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostPreViewSerializer

    filter_backends = [filters.OrderingFilter]

    ordering_fields = ['created', 'likes_count','updated']
    ordering = ['-created']

    def get_queryset(self):
        tag_name = self.kwargs.get('tag')
        search = Post.objects.filter(tags__title__iexact=tag_name)
        return search.filter(
            status=Post.STATUS_PUBLISHED).with_likes(self.request.user).with_saved_status(self.request.user).with_view_count().with_comments_count().select_related('user').prefetch_related('tags')