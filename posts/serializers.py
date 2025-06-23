from rest_framework import serializers
from .models import Post, Tag, Media, validate_persian_slug
from accounts.serializers import UserPreViewSerializer
from django.utils.html import strip_tags

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['media']
        extra_kwargs = {
            'media': {'required': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        media = Media.objects.create(user=user, **validated_data)
        return media

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class PostPreViewSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    user = UserPreViewSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'slug', 'title', 'user', 'summary', 'tags', 'main_image', 'created', 'updated']
        
    def get_summary(self, obj):
        plain_text = strip_tags(obj.content)
        summary = plain_text[:75]
        if len(plain_text) > 75:
            summary = summary[:75] + ' ... '
        return summary

class PostViewSerializer(serializers.ModelSerializer):
    user = UserPreViewSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'user', 'content', 'tags', 'main_image', 'created', 'updated']

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'tags', 'main_image']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': True},
            'slug': {'required': True},
        }

    def validate_tags(self, value):
        for tag_title in value:
            validate_persian_slug(tag_title)
        return value

    def _handle_tags(self, post, tags_data):
        if tags_data is None:
            return

        existing_tags = Tag.objects.filter(title__in=tags_data)
        existing_titles = {tag.title for tag in existing_tags}
        new_titles = [title for title in tags_data if title not in existing_titles]

        if new_titles:
            new_tags = [Tag(title=title) for title in new_titles]
            Tag.objects.bulk_create(new_tags)

        all_tags = Tag.objects.filter(title__in=tags_data)
        post.tags.set(all_tags)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)
        self._handle_tags(post, tags_data)
        return post
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        self._handle_tags(instance, tags_data)
        return instance