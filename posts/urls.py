from django.urls import path
from .views import PostsView, PostCreateView , PostView  , UserPostsView

urlpatterns = [
   path('', PostsView.as_view(), name='posts'),
   path('<str:slug>/', PostView.as_view(), name='post'),
   path('<str:user>/' , UserPostsView.as_view(), name='user_posts'),
   path('create/' , PostCreateView.as_view(), name='post_create'),
]