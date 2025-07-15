from dj_rest_auth.registration.views import (
    RegisterView,
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
    UserDetailsView,
)
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from grid.users.views import (
    GoogleLogin,
    MemberRegisterView,
    TeamInviteView,
    UserSignupRouteView,
    email_confirm_redirect,
    password_reset_confirm_redirect,
)


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="rest_register"),
    path("me/", UserDetailsView.as_view(), name="rest_user_details"),
    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("register/resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("social/google/", GoogleLogin.as_view(), name="google-login"),
    path("signup/status/", UserSignupRouteView.as_view(), name="signup-status"),
    path("member/invite/", TeamInviteView.as_view(), name="team-invites"),
    path("member/register/", MemberRegisterView.as_view(), name="team-member-register"),
]
