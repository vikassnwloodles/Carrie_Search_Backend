import os
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import render
from .serializers import RegisterSerializer
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from django.utils.encoding import force_str  # force_text is deprecated
from rest_framework.permissions import IsAuthenticated
from .services.perplexity import call_perplexity_model
from rest_framework.generics import ListAPIView
from .models import SearchQuery, UserStripeSession
from .serializers import SearchQuerySerializer
import stripe
from rest_framework.parsers import MultiPartParser
from PyPDF2 import PdfReader
from docx import Document
from .utils import image_to_data_uri
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


def test_ui_view(request):
    return render(request, "index.html")


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # # Create UserProfile
            # UserProfile.objects.create(user=user)

            # Send verification email with frontend redirect link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # FRONTEND VERIFICATION LINK
            # Replace with your actual frontend domain
            backend_base_url = f"{BACKEND_BASE_URL}/verify-email"
            verification_url = f"{backend_base_url}/{uid}/{token}/"

            send_mail(
                subject="Verify your email",
                message=f"Click to verify your email: {verification_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response(
                {"message": "User created. Check your email to verify."}, status=201
            )

        return Response(serializer.errors, status=400)


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return redirect(f"https://{FRONTEND_DOMAIN}/?status=invalid")

        if default_token_generator.check_token(user, token):
            profile = UserProfile.objects.get(user=user)
            profile.is_verified = True
            profile.save()
            return redirect(f"https://{FRONTEND_DOMAIN}/?status=success")

        return redirect(f"https://{FRONTEND_DOMAIN}/?status=expired")


class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse(
                    "password-reset-confirm", kwargs={"uidb64": uid, "token": token}
                )
            )

            send_mail(
                subject="Reset your password",
                message=f"Click the link below to reset your password:\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response(
                {"message": "Password reset link sent to your email"}, status=200
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"}, status=404
            )


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid or expired link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "New password is required"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset successfully"}, status=200)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            profile = UserProfile.objects.filter(user=user).first()
            if not profile or not profile.is_verified:
                return Response({"error": "Email not verified"}, status=403)

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )

        return Response({"error": "Invalid credentials"}, status=401)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except Exception as e:
            return Response(status=400)


# storing the promtpt & response & counting the number of prompts<25
# perplexity's part starts here
def get_best_model(model):
    return "sonar-pro" if model == "best" else model


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        image_url = request.data.get("image_url")
        model = request.data.get("model", "sonar-pro")
        return_images = request.data.get("return_images", False)
        search_mode = request.data.get("search_mode", "web")
        deep_research = request.data.get("deep_research", False)
        pro = request.data.get("pro", True)
        labs = request.data.get("labs", False)

        model = get_best_model(model)

        if not prompt and not image_url:
            return Response({"error": "Prompt or image is required."}, status=400)

        # Check if user is subscribed
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile or not profile.is_subscribed:
            # Apply search limit for non-subscribed users
            search_count = SearchQuery.objects.filter(user=request.user).count()
            if search_count >= int(os.getenv("FREE_SEARCH_LIMIT", 10)):
                return Response(
                    {"error": "Free search limit reached. Please subscribe."},
                    status=402,
                )

        result = call_perplexity_model(
            prompt=prompt,
            image_url=image_url,
            model=model,
            return_images=return_images,
            search_mode=search_mode,
            deep_research=deep_research,
        )

        SearchQuery.objects.create(
            user=request.user, prompt=prompt or "[Image]", response=result
        )

        return Response(result)


# library functionality


class LibraryView(ListAPIView):
    serializer_class = SearchQuerySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SearchQuery.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )[:10]


# pricing views

stripe.api_key = settings.STRIPE_SECRET_KEY


def check_subscription(user):
    try:
        user_stripe = UserStripeSession.objects.get(user=user)
        customer_id = user_stripe.stripe_customer_id

        # Fetch subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, status='all', limit=1)

        if subscriptions.data:
            subscription = subscriptions.data[0]
            is_active = subscription.status in ['active', 'trialing']
            return is_active
        else:
            return False
    except UserStripeSession.DoesNotExist:
        return False


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            # Fix for multiple UserStripeSession rows per user
            existing_session = UserStripeSession.objects.filter(user=user).first()

            # [TODO] ALREADY SUBSCRIBED
            is_active = check_subscription(user)
            if is_active:
                return Response({"subscription_status": "active", "checkout_url": None})

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
                success_url="https://"
                + os.getenv("FRONTEND_DOMAIN")
                + "?success=true&session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://" + os.getenv("FRONTEND_DOMAIN") + "?success=false",
            )

            # user_stripe_session = UserStripeSession(
            #     user=request.user, checkout_session_id=checkout_session.id
            # )
            user_stripe_session.checkout_session_id = checkout_session.id
            user_stripe_session.save()

            return Response({"subscription_status": "inactive", "checkout_url": checkout_session.url})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    print("🔔 Stripe webhook hit")

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if sig_header is None:
        print("❌ No Stripe signature header.")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print("❌ Invalid payload:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("❌ Signature verification failed:", e)
        return HttpResponse(status=400)

    print(f"✅ Event type: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        print(f"✅ Checkout session completed for {customer_email}")

        try:
            user = User.objects.get(email=customer_email)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_subscribed = True
            profile.save()
            print(f"✅ Subscription activated for {user.username}")
        except User.DoesNotExist:
            print("❌ No user found with that email.")
        except Exception as e:
            print(f"🔥 Error updating user subscription: {str(e)}")

    return HttpResponse(status=200)


class StripeSessionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            is_active = check_subscription(request.user)
            if is_active:
                return Response({"subscription_status": "active"})
            else:
                return Response({"subscription_status": "inactive"})

        except UserStripeSession.DoesNotExist:
            return Response({"subscription_status": "inactive"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UploadImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "No image uploaded"}, status=400)

        try:
            data_uri = image_to_data_uri(image)
            return Response({"image_url": data_uri}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UploadDocExtractView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=400)

        try:
            text = self.extract_text(uploaded_file)
            return Response({"text_content": text}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def extract_text(self, file):
        if file.name.endswith(".txt"):
            return file.read().decode("utf-8")

        elif file.name.endswith(".pdf"):
            reader = PdfReader(file)
            text = "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
            return text.strip()

        elif file.name.endswith(".docx"):
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        else:
            raise ValueError(
                "Unsupported file format. Please upload a .txt, .pdf, or .docx file."
            )
