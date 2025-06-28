from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserStripeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_stripe_session")
    checkout_session_id = models.TextField()
    stripe_customer_id = models.TextField()
    status = models.BooleanField(null=True, blank=True)
    payment_period = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user.username} at {self.created_at}"