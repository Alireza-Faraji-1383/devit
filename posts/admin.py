from django.contrib import admin
from .models import Post , Tag , LikePost , Comment , VoteComment

# Register your models here.

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(LikePost)