from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email

from .models import SearchQuery, UserProfile



class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['id', 'prompt', 'response', 'created_at']



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = UserProfile
        exclude = ['user']

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
            # Check UserProfile and its isactive field
            if hasattr(user, 'userprofile') and user.userprofile.is_verified:
                raise serializers.ValidationError("This username is already taken.")
        except User.DoesNotExist:
            pass  # Username does not exist, so it's fine
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate_email(self, value):
        try:
            validate_email(value)
            user = User.objects.filter(email__iexact=value).order_by("-id").first()
            if user:
                userprofile = UserProfile.objects.filter(user=user).order_by("-id").first()
                if userprofile:
                    if userprofile.is_verified == True:
                        raise serializers.ValidationError("This email is already taken.")
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        # Extract and remove password safely
        password = validated_data.pop("password")

        # Extract user-related fields
        username = validated_data.get("username")
        email = validated_data.get("email")

        user_fields = {
            "username": username,
            "email": email,
        }

        profile_fields = validated_data.copy()

        # Create or update user (excluding password in defaults)
        user, created = User.objects.update_or_create(
            username=username,
            defaults=user_fields
        )

        # Always set password securely
        user.set_password(password)
        user.save()

        # Update profile fields
        profile = user.userprofile  # Assumes OneToOneField from UserProfile to User
        for key, value in profile_fields.items():
            setattr(profile, key, value)
        profile.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        # Update core user fields
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # Update password if provided
        if password:
            instance.set_password(password)
            instance.save()

        # Update profile fields
        profile = instance.userprofile
        for key, value in validated_data.items():
            setattr(profile, key, value)
        profile.save()

        return instance
