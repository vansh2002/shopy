from rest_framework import serializers
from shopy.settings import AUTH_USER_MODEL
from .models import *
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'cart']
    

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        # Hash the password using make_password
        password = make_password(validated_data['password'])
        validated_data['password'] = password
        return super(RegisterSerializer, self).create(validated_data)

