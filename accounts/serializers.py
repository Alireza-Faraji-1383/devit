from .models import User
from rest_framework.serializers import ModelSerializer

class UserAuthSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['username','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

