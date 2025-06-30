from django.urls import path
from .views import (
    RegisterView,
    UploadDocExtractView,
    UploadImageView,
    LoginView,
    LogoutView,
    SearchView,
    LibraryView,
    PasswordResetConfirmView,
    RequestPasswordResetView,
    UserProfileView,
    UserProfileUpdateView,
    ChangePasswordView
)

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("search/", SearchView.as_view(), name="search"),
    path("library/", LibraryView.as_view(), name="library"),
    path("upload-image/", UploadImageView.as_view(), name="upload-image"),
    path("upload-doc/", UploadDocExtractView.as_view(), name="upload-doc"),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("user/fetch-profile/", UserProfileView.as_view(), name="user-profile"),
    path('user/update-profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
