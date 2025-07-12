from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.db.models import Count, Exists, OuterRef
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager


class UserQuerySet(models.QuerySet):
    def with_follow_info(self, user):

        is_follow = models.Value(None, output_field=models.BooleanField())

        if user and user.is_authenticated:
            is_follow = Exists(Follow.objects.filter(follower=user,followed=OuterRef('pk')))
            
        return self.annotate(
            followers_count=Count('following_relations', distinct=True),
            following_count=Count('follower_relations', distinct=True),
            is_follow=is_follow
        )
    

class UserManager(DjangoUserManager):
    pass


class User(AbstractUser):
    
    email = models.EmailField(unique=True)

    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    avatar = ProcessedImageField(upload_to='avatars/%Y/%m', blank=True, null=True, default='default/default_avatar.jpg',
        processors=[ResizeToFit(600, 600)],
        format='JPEG',
        options={'quality': 70},)
    
    objects = UserManager.from_queryset(UserQuerySet)()

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
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')
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