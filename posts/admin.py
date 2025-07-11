from django.contrib import admin
from .models import Post , Tag , LikePost , Comment , VoteComment , SavedPost , PostView

# Register your models here.

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(LikePost)
admin.site.register(Comment)
admin.site.register(VoteComment)
admin.site.register(SavedPost)
admin.site.register(PostView)