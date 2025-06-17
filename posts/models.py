from django.db import models
from accounts.models import User

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.core.exceptions import ValidationError
import re

class Post(models.Model):

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,max_length=100 ,)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    main_image = ProcessedImageField(upload_to='posts/%Y/%m', blank=True, null=True,
        processors=[ResizeToFit(600, 600)],
        format='JPEG',
        options={'quality': 70},)
    

    content = models.TextField()

    tags = models.ManyToManyField('Tag', related_name='posts' , blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = ' پست ها'


    def __str__(self):
        return self.title +  " توسط " + self.user.username
    


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
    

class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.FileField(upload_to='media/%Y/%m', blank=True, null=True)
    slug = models.SlugField(max_length=100 , unique=True , default="media")
    