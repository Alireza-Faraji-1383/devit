from django.db import models
from posts.models import Post
from accounts.models import User

# Create your models here.

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    is_resolved = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        
        return self.post + ':' + self.content
    


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' پست ' + self.post + ' لایک کرده است'