from rest_framework import serializers
from .models import SearchQuery
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError



class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['id', 'prompt', 'response', 'created_at']



from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    # Extended profile fields
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.CharField(required=False, allow_blank=True)
    preferred_pronouns = serializers.CharField(required=False, allow_blank=True)
    mobile_phone_number = serializers.CharField(required=False, allow_blank=True)
    home_address = serializers.CharField(required=False, allow_blank=True)

    race_ethnicity = serializers.CharField(required=False, allow_blank=True)
    household_income_range = serializers.CharField(required=False, allow_blank=True)
    marital_status = serializers.CharField(required=False, allow_blank=True)
    number_of_people_in_household = serializers.IntegerField(required=False)
    is_employed = serializers.BooleanField(required=False)
    is_student = serializers.BooleanField(required=False)
    has_computer_or_internet = serializers.BooleanField(required=False)

    agreed_to_terms = serializers.BooleanField(required=False)
    consent_to_communications = serializers.BooleanField(required=False)

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
