from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

class User(AbstractUser):
    
    email = models.EmailField(unique=True)

    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    avatar = models.ImageField(upload_to='avatars/%Y/%m', blank=True, null=True)

    def __str__(self):
        return self.username
    


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_code')
    code = models.CharField(max_length=7 , unique=True)
    
    is_used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


    def is_expired(self):
        return bool(timezone.now() > (self.created + timedelta(minutes=2)))

    def __str__(self):
        return self.code + " : " + self.user.username

    
    


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'followed'], name='unique_follow')
        ]

    def save(self, *args, **kwargs):
        if self.follower == self.followed:
            raise ValidationError('نمیتونی خودتو فالو کنی')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'کاربر {self.follower.username} دنبال کرده {self.followed.username}'