# urls.py
from django.urls import path
from .views import (
    CancelSubscriptionView,
    CreateCheckoutSessionView,
    StripeSessionStatusView,
    create_stripe_portal_session,
    stripe_webhook
)

urlpatterns = [
    path(
        "cancel-subscription/",
        CancelSubscriptionView.as_view(),
        name="cancel-subscription",
    ),
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("get-pro-status/", StripeSessionStatusView.as_view(), name="get-pro-status"),
    path("stripe-portal/", create_stripe_portal_session, name="stripe-portal"),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]
