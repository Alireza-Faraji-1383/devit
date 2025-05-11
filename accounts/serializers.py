from .models import User , Follow
from rest_framework import serializers

class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']
        extra_kwargs = {'password': {'write_only': True,'required': True},
                        'username': {'required': True},
                        }



class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['pk','username','email','password']
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True},
                        'password': {'write_only': True , 'required': True},
                        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    


class UserInfoSerializer(serializers.ModelSerializer):

    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User    
        fields = ['pk','username','email', 'first_name', 'last_name', 'bio', 'gender', 'birthday', 'avatar','followers','following']
        
        extra_kwargs = {

            'username': {'read_only': True},
            'email': {'read_only': True},
            'followers': {'read_only': True},
            'following': {'read_only': True},

        }

    def get_followers(self, obj):
        return obj.followers.count()
        
    def get_following(self, obj):
        return obj.following.count()
    


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['pk','follower','following']
        extra_kwargs = {'follower': {'required': True},
                        'following': {'required': True},
                        }
