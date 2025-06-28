import stripe
from datetime import datetime, timezone


def check_subscription(user_stripe):
    is_active = False

    if user_stripe:
        customer_id = user_stripe.stripe_customer_id

        # Fetch subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, status='all', limit=1)

        if subscriptions.data:
            subscription = subscriptions.data[0]
            is_active = subscription.status in ['active', 'trialing']
    
    return is_active


def timestamp2utc(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)