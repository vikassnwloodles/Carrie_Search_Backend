# urls.py
from django.urls import path
from .views import CancelSubscriptionView, CreateCheckoutSessionView, StripeSessionStatusView

urlpatterns = [
    path("cancel-subscription/", CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('get-pro-status/', StripeSessionStatusView.as_view(), name='get-pro-status'),
]
