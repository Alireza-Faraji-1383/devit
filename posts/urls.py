from django.urls import path
from .views import  (MediaCreateView , PostDetailView , PostListCreateView , UserPostsView , PostLikeView
                     ,CommentDetailView , CommentListCreateView , CommentVoteView ,CommentRepliesListView
                     ,PostSaveToggleView , SavedPostListView , PostTagListView , TagListView
                     )

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    
    path('saved/', SavedPostListView.as_view(), name='saved-post-list'),
    
    path('media/create/', MediaCreateView.as_view(), name='media-create'),
    path('user/<str:user>/', UserPostsView.as_view(), name='user-posts-list'),

    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<str:tag>/', PostTagListView.as_view(), name='post-tag-list'),
    
    path('<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('<slug:slug>/like/', PostLikeView.as_view(), name='post-like-toggle'),
    path('<slug:slug>/save/', PostSaveToggleView.as_view(), name='post-save-toggle'),
    path('<slug:slug>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/vote/', CommentVoteView.as_view(), name='comment-vote'),
    path('comments/<int:pk>/replies/', CommentRepliesListView.as_view(), name='comment-replies-list'),
]