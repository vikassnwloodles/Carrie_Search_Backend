import stripe
from datetime import datetime, timezone


def check_subscription(user_stripe):
    subscription_status = "inactive"
    next_renewal_time = None
    cancel_at = None

    if user_stripe:
        customer_id = user_stripe.stripe_customer_id

        # Fetch subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, status='all', limit=1)

        if subscriptions.data:
            subscription = subscriptions.data[0]
            is_active = subscription.status in ['active', 'trialing']
            if is_active:
                subscription_status = "active"
                if subscription.cancel_at_period_end == True:
                    cancel_at = timestamp2utc(subscription.cancel_at)
                else:
                    next_renewal_time = timestamp2utc(subscription["items"].data[0].current_period_end)
    
    return subscription_status, next_renewal_time, cancel_at


def timestamp2utc(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)