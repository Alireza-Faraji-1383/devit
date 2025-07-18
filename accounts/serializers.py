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
        })
    
    class Meta:
        model = User
        fields = ['username','email','password']
        extra_kwargs = {'username': {'required': True},      
                        'password': {'write_only': True , 'required': True},
                        }
        
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return value
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserInfoSerializer(serializers.ModelSerializer):

    followers = serializers.IntegerField(source='followers_count', read_only=True)
    following = serializers.IntegerField(source='following_count', read_only=True)
    is_follow = serializers.BooleanField(read_only=True, allow_null=True)

    avatar = serializers.ImageField(required=False)


    class Meta:
        model = User    
        fields = ['username','email','password', 'first_name', 'last_name', 'bio', 'gender', 'birthday', 'avatar','banner','followers','following','is_follow']
        
        extra_kwargs = {

            # 'username': {'read_only': True},
            'password': {'write_only': True},
            'email': {'read_only': True},
        }
    
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


class UserPreViewSerializer(serializers.ModelSerializer):

    is_follow = serializers.BooleanField(allow_null=True, read_only = True)

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name','avatar','is_follow']

    

class PasswordResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError('تایپ شده رمز عبور ها مطابقت ندارند')
        return data
    

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['pk','follower','following']
        extra_kwargs = {'follower': {'required': True},
                        'following': {'required': True},
                        }
