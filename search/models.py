from django.db import models
from django.contrib.auth.models import User

class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_queries")
    prompt = models.TextField()
    response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user.username} at {self.created_at}"
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False) 

    # Personal Information
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    preferred_pronouns = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile_phone_number = models.CharField(max_length=20, null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)

    # Account & Access
    username = models.CharField(max_length=150, null=True, blank=True)

    # Consent
    agreed_to_terms = models.BooleanField(null=True, blank=True)
    consent_to_communications = models.BooleanField(null=True, blank=True)

    # Demographic Information
    race_ethnicity = models.CharField(max_length=100, null=True, blank=True)
    household_income_range = models.CharField(max_length=100, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    number_of_people_in_household = models.PositiveIntegerField(null=True, blank=True)
    is_employed = models.BooleanField(null=True, blank=True)
    is_student = models.BooleanField(null=True, blank=True)
    has_computer_or_internet = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} Profile"

