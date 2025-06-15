from django.urls import path
from .views import PostsView, PostCreateView , PostView

urlpatterns = [
   path('', PostsView.as_view(), name='posts'),
   path('<int:id>/', PostView.as_view(), name='post'),
   path('create/' , PostCreateView.as_view(), name='post_create'),
]