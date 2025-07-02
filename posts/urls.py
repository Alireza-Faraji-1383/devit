from django.urls import path
from .views import  (MediaCreateView , PostDetailView , PostListCreateView , UserPostsView , PostLikeView
                     ,CommentDetailView , CommentListCreateView , CommentVoteView ,CommentRepliesListView
                     )

urlpatterns = [

    # URL برای لیست تمام پست‌ها و ساخت یک پست جدید
    path('', PostListCreateView.as_view(), name='post-list-create'),

    # URL برای نمایش، آپدیت و حذف یک پست خاص با استفاده از slug
    path('<slug:slug>/', PostDetailView.as_view(), name='post-detail'),

    # URL برای نمایش پست‌های یک کاربر خاص
    path('user/<str:user>/', UserPostsView.as_view(), name='user-posts-list'),

    # لایک یک پست با استفاده از slug
    path('<slug:slug>/like',PostLikeView.as_view(),name='post_like'),

    # ساخت و لیست کامنت های یک پست با اسلاگ
    path('<slug:slug>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    
    # ویرایش و حذف یک کامنت خاص با استفاده از ID آن
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    
    # رای دادن (لایک/دیسلایک) به یک کامنت خاص
    path('comments/<int:pk>/vote/', CommentVoteView.as_view(), name='comment-vote'),

    # ریپلای های یک ریپلای خاص
    path('comments/<int:pk>/replies/', CommentRepliesListView.as_view(), name='comment-replies-list'),
]