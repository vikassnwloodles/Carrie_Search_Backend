from django.urls import path
from .views import RegisterView, UploadDocExtractView, UploadImageView, LoginView, LogoutView,SearchView, LibraryView, PasswordResetConfirmView, RequestPasswordResetView

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("search/", SearchView.as_view(), name="search"),
    path("library/", LibraryView.as_view(), name="library"),
    path("upload-image/", UploadImageView.as_view(), name="upload-image"),
    path("upload-doc/", UploadDocExtractView.as_view(), name="upload-doc"),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
