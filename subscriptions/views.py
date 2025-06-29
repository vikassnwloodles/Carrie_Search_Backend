from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import UserStripeSession
from .utils import check_subscription, timestamp2utc

stripe.api_key = settings.STRIPE_SECRET_KEY
FRONTEND_BASE_URL = settings.FRONTEND_BASE_URL


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            # Get the latest subscription (you can adjust this logic as needed)
            session = (
                UserStripeSession.objects.filter(
                    user=user, stripe_customer_id__isnull=False
                )
                .order_by("-id")
                .first()
            )
            if session:
                subscription_id = session.stripe_customer_id
                subscriptions = stripe.Subscription.list(
                    customer=subscription_id, status="all", limit=1
                )

            if session and subscriptions.data:
                subscription = subscriptions.data[0]
                if subscription.status == "canceled":
                    return Response(
                        {
                            "message": "Subscription cancellation complete.",
                            "subscription_status": subscription.status,
                            "cancel_at": subscription.cancel_at
                        }
                    )
                elif subscription.cancel_at_period_end == True:
                    return Response(
                        {
                            "message": "Subscription cancellation scheduled.",
                            "subscription_status": subscription.status,
                            "cancel_at": timestamp2utc(subscription.cancel_at)
                        }
                    )
                
                # Cancel at period end (or delete for immediate cancellation)
                canceled_subscription = stripe.Subscription.modify(
                    subscription.id,
                    cancel_at_period_end=True,  # Set to False or use delete() for immediate cancel
                )
                return Response(
                    {
                        "message": "Subscription cancellation scheduled.",
                        "subscription_status": canceled_subscription.status,
                        "cancel_at": canceled_subscription.cancel_at
                    }
                )

            return Response(
                {
                    "message": "No active subscription found.",
                    "subscription_status": None,
                }
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            # Fix for multiple UserStripeSession rows per user
            existing_session = (
                UserStripeSession.objects.filter(user=user).order_by("-id").first()
            )

            if not existing_session:
                # Create a new Stripe customer and session entry
                customer = stripe.Customer.create(email=user.email)
                user_stripe_session = UserStripeSession.objects.create(
                    user=user,
                    checkout_session_id="",  # will update after session creation
                )
                user_stripe_session.stripe_customer_id = customer.id
                user_stripe_session.save()
            else:
                is_subscribed = user.userprofile.is_subscribed
                if is_subscribed:
                    # ALREADY SUBSCRIBED
                    return Response(
                        {"subscription_status": "active", "checkout_url": None}
                    )

                # Retrieve customer using existing stripe_customer_id
                customer = stripe.Customer.retrieve(existing_session.stripe_customer_id)
                user_stripe_session = existing_session

            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": settings.STRIPE_PRICE_ID,
                        "quantity": 1,
                    }
                ],
                # customer_email=request.user.email,
                # customer_email="testuser@example.com",
                success_url=FRONTEND_BASE_URL
                + "?success=true&session_id={CHECKOUT_SESSION_ID}",
                cancel_url=FRONTEND_BASE_URL + "?success=false",
            )

            # user_stripe_session = UserStripeSession(
            #     user=request.user, checkout_session_id=checkout_session.id
            # )
            user_stripe_session.checkout_session_id = checkout_session.id
            user_stripe_session.save()

            return Response(
                {
                    "subscription_status": "inactive",
                    "checkout_url": checkout_session.url,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# class StripeSessionStatusView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             existing_session = (
#                 UserStripeSession.objects.filter(user=request.user)
#                 .order_by("-id")
#                 .first()
#             )
#             subscription_status, next_renewal_time, cancel_at = "inactive", None, None
#             if existing_session:
#                 subscription_status, next_renewal_time, cancel_at = check_subscription(existing_session)
#             if existing_session and subscription_status == "active":
#                 return Response({"subscription_status": subscription_status, "next_renewal_at":next_renewal_time, "cancel_at":cancel_at})
#             else:
#                 return Response({"subscription_status": subscription_status, "next_renewal_at":next_renewal_time, "cancel_at":cancel_at})
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
class StripeSessionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            userprofile = request.user.userprofile
            if userprofile:
                is_subscribed = userprofile.is_subscribed
            if userprofile and is_subscribed:
                return Response({"subscription_status": "active"})
            else:
                return Response({"subscription_status": "inactive"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_portal_session(request):
    user = request.user
    user_stripe_session = (
        user.user_stripe_session.all()
        .order_by("-id")
        .first()
    )

    if user_stripe_session is None:
        return Response({'error': f'No stripe session record found for {user.username}!'}, status=400)
    
    customer_id = user_stripe_session.stripe_customer_id

    if not customer_id:
        return Response({'error': 'User has no Stripe customer ID'}, status=400)

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=FRONTEND_BASE_URL,  # where to redirect after managing billing
        )
        return Response({'url': session.url})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    # ✅ Payment succeeded
    if event['type'] == 'invoice.paid':
        customer_id = event['data']['object']['customer']
        try:
            user_session = UserStripeSession.objects.get(stripe_customer_id=customer_id)
            userprofile = user_session.user.userprofile
            userprofile.is_subscribed = True
            userprofile.save()
        except UserStripeSession.DoesNotExist:
            pass

    # ❌ Subscription canceled or payment failed
    elif event['type'] in ['customer.subscription.deleted', 'invoice.payment_failed']:
        customer_id = event['data']['object']['customer']
        try:
            user_session = UserStripeSession.objects.get(stripe_customer_id=customer_id)
            userprofile = user_session.user.userprofile
            userprofile.is_subscribed = False
            userprofile.save()
        except UserStripeSession.DoesNotExist:
            pass

    return JsonResponse({'status': 'success'}, status=200)
