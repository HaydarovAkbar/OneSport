from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.serializers import JWTSerializer
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from grid.users.choices import InviteStatus
from grid.users.models import TeamInvite
from grid.users.permissions import CanSendTeamInvite
from grid.users.serializers import (
    MemberRegisterSerializer,
    RouteResponseSerializer,
    TeamInviteSerializer,
)
from grid.users.signup_router import Router


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/")


class GoogleLogin(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = config("GRID_API_SOCIAL_AUTH_GOOGLE_CALLBACK_URL")
    client_class = OAuth2Client

    @swagger_auto_schema(
        operation_summary="Log users in with google",
        operation_description="Endpoint to log users in using google",
        tags=["social"],
        request_body=SocialLoginSerializer,
        responses={status.HTTP_200_OK: openapi.Response(description="Successful login", schema=JWTSerializer)},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserSignupRouteView(APIView):
    """
    Get signup routing information for the current user
    Returns route, message, role of user and uuid of the signup profile
    role : recruiter, uuid -> recruiter model
    role : client, uuid -> client model
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RouteResponseSerializer

    def get(self, request, *args, **kwargs):
        route, message, profile = Router.get_route(self.request.user)
        response_data = {
            "route": route,
            "message": message,
            "role": self.request.user.role,
            # uuid is to identify the recruiter or client profile object
            "uuid": str(profile.uuid) if profile else None,
            "is_member": self.request.user.is_team_member,
        }
        serializer = self.serializer_class(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TeamInviteView(APIView):
    permission_classes = [IsAuthenticated, CanSendTeamInvite]
    serializer_classes = [TeamInviteSerializer]

    @swagger_auto_schema(
        operation_summary="Create team invite",
        operation_description="Send an invitation to a team member",
        request_body=TeamInviteSerializer,
        responses={
            201: openapi.Response(description="Invite created successfully", schema=TeamInviteSerializer),
            400: openapi.Response(
                description="Bad request",
                examples={"application/json": {"error": "A pending invitation already exists for this email"}},
            ),
            500: openapi.Response(
                description="Server error", examples={"application/json": {"error": "Failed to send invitation email"}}
            ),
        },
        tags=["Team"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = TeamInviteSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            # Check if email already has a pending invite
            if TeamInvite.objects.filter(
                email=serializer.validated_data["email"], status=InviteStatus.PENDING
            ).exists():
                return Response(
                    {"error": "A pending invitation already exists for this email"}, status=status.HTTP_400_BAD_REQUEST
                )
            invite = serializer.save()

            # Get inviter's name based on their role
            if invite.inviter.is_client:
                inviter_name = (
                    f"{invite.inviter.clientuserprofile.first_name} {invite.inviter.clientuserprofile.last_name}"
                )
                company_name = invite.inviter.clientuserprofile.client.company_name
            else:
                inviter_name = f"{invite.inviter.recruiter.first_name} {invite.inviter.recruiter.last_name}"
                company_name = invite.inviter.recruiter.agency.agency_name

            # Prepare email context
            context = {
                "inviter_name": inviter_name,
                "company_name": company_name,
                "invite_link": f"{settings.FRONTEND_URL}/invite/{invite.token}",
                "user_type": invite.data["user_type"],
            }

            html_message = render_to_string("users/team_invite.html", context)

            send_mail(
                subject=f"Join {company_name} as a team member",
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invite.email],
                html_message=html_message,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberRegisterView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Register team member",
        operation_description="Create user account from invitation token",
        request_body=MemberRegisterSerializer,
        responses={
            201: openapi.Response(
                description="Account created successfully",
                examples={"application/json": {"detail": "Account created successfully"}},
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "token": ["Invalid or expired invitation token"],
                        "password1": ["This password is too common."],
                        "non_field_errors": ["The two password fields didn't match."],
                    }
                },
            ),
        },
        tags=["Team"],
    )
    def post(self, request):
        serializer = MemberRegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"detail": "Account created successfully"}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
