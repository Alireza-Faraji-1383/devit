from django.urls import path
from .views import  MediaCreateView , PostDetailView , PostListCreateView , UserPostsView

urlpatterns = [

    # URL برای لیست تمام پست‌ها و ساخت یک پست جدید
    # GET /api/posts/ -> لیست پست‌ها را برمی‌گرداند (توسط ListCreateAPIView)
    # POST /api/posts/ -> یک پست جدید می‌سازد (توسط ListCreateAPIView)
    path('', PostListCreateView.as_view(), name='post-list-create'),

    # URL برای نمایش، آپدیت و حذف یک پست خاص با استفاده از slug
    # GET /api/posts/<slug>/ -> نمایش یک پست (توسط RetrieveUpdateDestroyAPIView)
    # PUT /api/posts/<slug>/ -> آپدیت کامل یک پست
    # PATCH /api/posts/<slug>/ -> آپدیت بخشی از یک پست
    # DELETE /api/posts/<slug>/ -> حذف یک پست
    path('<slug:slug>/', PostDetailView.as_view(), name='post-detail'),

    # URL برای نمایش پست‌های یک کاربر خاص
    # GET /api/posts/user/<username>/
    path('user/<str:user>/', UserPostsView.as_view(), name='user-posts-list'),
]