from rest_framework import serializers
from .models import Post , Tag , validate_persian_slug

class PostPreViewSerializer(serializers.ModelSerializer):

    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id','title','user','tags','main_image','created','updated'
                  ]
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['tags'] = [tag.title for tag in instance.tags.all()]
        return rep
        

class PostViewSerializer(serializers.ModelSerializer):

    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id','title','user','content','tags','main_image','created','updated']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['tags'] = [tag.title for tag in instance.tags.all()]
        return rep        


class PostCreateSerializer(serializers.ModelSerializer):

    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True
    )

    class Meta:
        model = Post
        fields = ['title','content','tags','main_image',]
        extra_kwargs = {

            'title': {'required': True},
            'content': {'required': True},
        }

    def validate_tags(self, value):
        for tag_title in value:
            validate_persian_slug(tag_title)
        return value

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)

        for tag_title in tags_data:
            tag, _ = Tag.objects.get_or_create(title=tag_title)
            post.tags.add(tag)

        return post
