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



class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    # Extended fields (profile)
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

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    # def create(self, validated_data):
    #     filter_validated_data = dict()
    #     filter_validated_data["username"] = validated_data["username"]
    #     filter_validated_data["email"] = validated_data["email"]
    #     filter_validated_data["password"] = validated_data["password"]
    #     return User.objects.create_user(**filter_validated_data)

    def create(self, validated_data):
        # Separate user and profile data
        user_fields = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "password": validated_data.pop("password"),
        }

        profile_fields = validated_data.copy()

        user = User.objects.create_user(**user_fields)

        # Update profile fields
        profile = user.userprofile
        for key, value in profile_fields.items():
            setattr(profile, key, value)
        profile.save()

        return user