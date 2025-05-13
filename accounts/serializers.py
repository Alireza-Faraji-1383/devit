from .models import User , Follow
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserAuthSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)



class UserRegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="این ایمیل قبلاً ثبت شده است.")],
        error_messages={
            'required': 'لطفاً ایمیل را وارد کنید.',
            'invalid': 'فرمت ایمیل وارد شده نادرست است.',
        }
    )


    class Meta:
        model = User
        fields = ['pk','username','email','password']
        extra_kwargs = {'username': {'required': True},      
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
        fields = ['username','email','password', 'first_name', 'last_name', 'bio', 'gender', 'birthday', 'avatar','followers','following']
        
        extra_kwargs = {

            # 'username': {'read_only': True},
            'password': {'write_only': True},
            'email': {'read_only': True},
            'followers': {'read_only': True},
            'following': {'read_only': True},

        }

    def get_followers(self, obj):
        return obj.followers.count()
        
    def get_following(self, obj):
        return obj.following.count()
    
    def to_internal_value(self, data):
        unknown_fields = set(data.keys()) - set(self.fields.keys())
        if "email" in data.keys():
            unknown_fields.add("email")
        if unknown_fields:
            raise serializers.ValidationError({
                "detail": f"فیلدهای نامعتبر ارسال شده‌اند: {', '.join(unknown_fields)}"
            })
        
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['pk','follower','following']
        extra_kwargs = {'follower': {'required': True},
                        'following': {'required': True},
                        }
