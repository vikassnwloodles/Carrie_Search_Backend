from django.urls import path
from .views import RegisterView, UploadDocExtractView, UploadImageView, StripeSessionStatusView, LoginView, LogoutView,SearchView, LibraryView, CreateCheckoutSessionView, PasswordResetConfirmView, RequestPasswordResetView

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("search/", SearchView.as_view(), name="search"),
    path("library/", LibraryView.as_view(), name="library"),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("upload-image/", UploadImageView.as_view(), name="upload-image"),
     path("upload-doc/", UploadDocExtractView.as_view(), name="upload-doc"),
     path('get-pro-status/', StripeSessionStatusView.as_view(), name='get-pro-status'),

     path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

]
