from rest_framework import serializers
from .models import Customer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id','first_name','last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
        
    def validate_email(self, value):
        EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(EMAIL_REGEX, value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_password(self, value):
        PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(PASSWORD_REGEX, value):
            raise serializers.ValidationError("Password must be at least 8 characters long, contain at least one letter and one number.")
        return value
    
   
    def validate_first_name(self, value):
        NAME_REGEX = r'^[A-Za-z\s]+$'
        if not re.match(NAME_REGEX, value):
            raise serializers.ValidationError("First name should contain only letters and spaces.")
        if value[0].islower():
            raise serializers.ValidationError("The first letter of the first name should be capital.")
        return value


    def validate_last_name(self, value):
        NAME_REGEX = r'^[A-Za-z\s]+$'
        if not re.match(NAME_REGEX, value):
            raise serializers.ValidationError("Last name should contain only letters and spaces.")
        if value[0].islower():
            raise serializers.ValidationError("The first letter of the last name should be capital.")
        return value
    


    def create(self, validated_data):
        user = Customer.objects.create_user(
            first_name = validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        
        if not user:
            raise AuthenticationFailed("Invalid credentials, please try again.")
        
        # Check if the user is verified
        if not user.is_verified:
            raise AuthenticationFailed("Your email is not verified. Please verify your email first.")
        
        # Store the authenticated user in the context for access in views
        self.context['user'] = user
        
        return data

        