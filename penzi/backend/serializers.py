from rest_framework import serializers
from .models import User, ReceivedMessage, UserProfile, UserDetails, UserDescription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'is_registered')

class ReceivedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivedMessage
        fields = ('id', 'user', 'message', 'timestamp')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'age', 'gender', 'county', 'town')

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ('id', 'user', 'level_of_education', 'profession', 'marital_status', 'religion', 'ethnicity')

class UserDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDescription
        fields = ('id', 'user', 'description_text')
