from django.urls import path
from .views import RegisterView, UploadDocExtractView, UploadImageView, StripeSessionStatusView, LoginView, LogoutView, SearchView, LibraryView, CreateCheckoutSessionView

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("search/", SearchView.as_view(), name="search"),
    path("library/", LibraryView.as_view(), name="library"),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("upload-image/", UploadImageView.as_view(), name="upload-image"),
     path("upload-doc/", UploadDocExtractView.as_view(), name="upload-doc"),
     path('subscription-status/', StripeSessionStatusView.as_view(), name='subscription-status'),


]
