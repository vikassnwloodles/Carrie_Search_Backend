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

    def __str__(self):
        return f"{self.user.username} Profile"

