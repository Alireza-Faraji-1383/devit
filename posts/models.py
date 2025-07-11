from django.db import models
from accounts.models import User
from django.db.models import Q, Count, Exists, OuterRef, Subquery

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.core.exceptions import ValidationError
import re



class PostQuerySet(models.QuerySet):

    def visible_to(self, user):
        """فقط پست‌هایی را برمی‌گرداند که برای کاربر فعلی قابل مشاهده هستند."""
        if user and user.is_authenticated:
            return self.filter(Q(status=Post.STATUS_PUBLISHED) | Q(user=user)).distinct()
        return self.filter(status=Post.STATUS_PUBLISHED)

    def with_likes(self, user):
        """اطلاعات لایک (تعداد و وضعیت) را به کوئری اضافه می‌کند."""
        is_liked_value = models.Value(None, output_field=models.BooleanField())
        if user and user.is_authenticated:
            is_liked_subquery = LikePost.objects.filter(post=OuterRef('pk'), user=user)
            is_liked_value = Exists(is_liked_subquery)
        
        return self.annotate(
            likes_count=Count('likes', distinct=True),
            is_like=is_liked_value
        )

    def with_saved_status(self, user):
        """وضعیت ذخیره شدن پست توسط کاربر را به کوئری اضافه می‌کند."""
        is_saved_value = models.Value(None, output_field=models.BooleanField())
        if user and user.is_authenticated:
            is_saved_subquery = SavedPost.objects.filter(post=OuterRef('pk'), user=user)
            is_saved_value = Exists(is_saved_subquery)
        return self.annotate(is_saved=is_saved_value)
    
    def with_view_count(self):
        """ تعداد مشاهده های پست را به کوئری اضافه می‌کند."""
        return self.annotate(
            view_count=Count('views', distinct=True)
        )

class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def with_likes(self, user):
        return self.get_queryset().with_likes(user)

    def with_saved_status(self, user):
        return self.get_queryset().with_saved_status(user)
    
    def with_view_count(self):
        return self.get_queryset().with_view_count()


class Post(models.Model):

    STATUS_PENDING = 'Pending'
    STATUS_PUBLISHED = 'Published'
    STATUS_CHOICES = (
        (STATUS_PUBLISHED, 'منتشر شده'),
        (STATUS_PENDING, 'منتظر انتشار')
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,max_length=100 ,)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    main_image = ProcessedImageField(upload_to='posts/%Y/%m', blank=True, null=True,
        processors=[ResizeToFit(600, 600)],
        format='JPEG',
        options={'quality': 70},)
    

    content = models.TextField()

    tags = models.ManyToManyField('Tag', related_name='posts' , blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PostManager()

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = ' پست ها'


    def __str__(self):
        return self.title +  " توسط " + self.user.username
    
    def save(self, *args, **kwargs):
        self.slug = self.slug.lower()
        super().save(*args, **kwargs)
    


def validate_persian_slug(value):
    pattern = r'^[a-zA-Z0-9_\u0600-\u06FF-]+$'  # \u0600-\u06FF برای حروف فارسی
    if not re.match(pattern, value):
        raise ValidationError(
            'تگ فقط می‌تواند شامل حروف فارسی و انگلیسی، اعداد، خط تیره (-) و زیرخط (_) باشد.'
        )


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True, validators=[validate_persian_slug])


    class Meta:
        verbose_name = 'تگ'
        verbose_name_plural = 'تگ ها'

    def __str__(self):
        return self.title

class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE ,related_name='likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'لایک'
        verbose_name_plural = 'لایک ها'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_like_per_user_post')
        ]
        ordering = ['-created']

    def __str__(self):
        return self.user.username +  ' پست ' + self.post.title +' لایک کرده است.'


class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.FileField(upload_to='media/%Y/%m', blank=True, null=True)
    # slug = models.SlugField(max_length=100 , unique=True , default="media")
    


class CommentQuerySet(models.QuerySet):
    def with_votes(self, user):
        """اطلاعات کامل رای‌ها (لایک/دیسلایک) را به کوئری کامنت اضافه می‌کند."""
        likes = Count('votes', filter=models.Q(votes__vote=VoteComment.LIKE))
        dislikes = Count('votes', filter=models.Q(votes__vote=VoteComment.DISLIKE))
        
        user_vote = models.Value(None, output_field=models.IntegerField())
        if user and user.is_authenticated:
            user_vote_subquery = VoteComment.objects.filter(
                comment=OuterRef('pk'),
                user=user
            ).values('vote')[:1]
            user_vote = Subquery(user_vote_subquery, output_field=models.IntegerField(null=True))

        return self.annotate(
            likes_count=likes,
            dislikes_count=dislikes,
            user_vote=user_vote
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'
        ordering = ['created']

    def __str__(self):
        return f'Comment by {self.user.username} on post "{self.post.title}"'


class VoteComment(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    
    class Meta:
        verbose_name = 'رای کامنت'
        verbose_name_plural = 'رای کامنت ها'
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_vote_per_user_comment')
        ]



class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ' سیو پست'
        verbose_name_plural = ' سیو پست ها'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_saved_post_per_user')
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username} سیو کرد پست "{self.post.title}"'



class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_views')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بازدید پست'
        verbose_name_plural = ' بازدید پست ها'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_view_per_user_post')
        ]
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.username} بازدید کرد پست  "{self.post.title}"'