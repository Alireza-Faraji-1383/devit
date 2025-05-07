from django.db import models
from accounts.models import User

class Post(models.Model):

    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    main_image = models.ImageField(upload_to='posts/%Y/%m', blank=True, null=True)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title +  " by " + self.user.username