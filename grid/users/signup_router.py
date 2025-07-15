from enum import Enum

from grid.clients.models import Client, ClientUserProfile
from grid.recruiters.models import Recruiter
from grid.users.models import User


class SignupStep(Enum):
    BASIC_INFO = "basic_info"
    AGENCY_INFO = "agency_info"
    DESCRIPTION = "description"


class Router:
    """
    Handles routing logic for all user types
    """

    @staticmethod
    def get_route(user: User) -> str:
        """Main routing function based on user type"""
        if user.is_team_member:
            return Router.get_member_route(user)
        elif user.is_recruiter:
            return Router.get_recruiter_signup_route(user)
        elif user.is_client:
            return Router.get_client_signup_route(user)
        elif user.is_admin:
            return "admin", "Admin Page", None

    @staticmethod
    def get_recruiter_signup_route(user: User):
        """
        Determines recruiter routing based on status
        Returns tuple of (route, message, recruiter_instance)
        """
        try:
            recruiter = Recruiter.objects.get(user=user)

            # Check terminal states first
            if recruiter.status == Recruiter.RecruiterStatus.ACTIVE:
                return "dashboard", "Your account is active", recruiter
            if recruiter.status == Recruiter.RecruiterStatus.PENDING_APPROVAL:
                return "pending_approval", "Your account is pending approval", recruiter
            elif recruiter.status == Recruiter.RecruiterStatus.REJECTED:
                return "rejected", "Your application has been rejected", recruiter
            elif recruiter.status == Recruiter.RecruiterStatus.WAIT_LIST:
                return "waitlist", "Your application is on the waitlist", recruiter

            # Handle signup steps
            if recruiter.status == Recruiter.RecruiterStatus.PENDING_SIGNUP:
                if not recruiter.agency:
                    return SignupStep.AGENCY_INFO.value, "Please complete agency information", recruiter
                return SignupStep.DESCRIPTION.value, "Please complete description step", recruiter

        except Recruiter.DoesNotExist:
            return SignupStep.BASIC_INFO.value, "Start your application", None

    @staticmethod
    def get_client_signup_route(user: User):
        """
        Determines client routing based on status
        Returns tuple of (route, message, client_instance)
        """
        try:
            client_user = ClientUserProfile.objects.get(user=user)
            client = client_user.client

            if not client:
                return SignupStep.BASIC_INFO.value, "Start your application", None

            if client.status == Client.Status.ACTIVE:
                return "dashboard", "Welcome back", client
            elif client.status == Client.Status.WAIT_LIST:
                return "waitlist", "Your application is on the waitlist", client
            elif client.status == Client.Status.REJECTED:
                return "rejected", "Your application has been rejected", client
            elif client.status == Client.Status.PENDING_APPROVAL:
                return "pending_approval", "Your application is under review", client
            elif client.status == Client.Status.PENDING_SIGNUP:
                return "company_info", "Please complete company information", client

        except ClientUserProfile.DoesNotExist:
            return SignupStep.BASIC_INFO.value, "Start your application", None

    @staticmethod
    def get_member_route(user: User):
        """
        Determines routing for team members
        Returns tuple of (route, message, member_instance)
        """
        if user.is_recruiter:
            try:
                member = Recruiter.objects.get(user=user)
                if member.status == Recruiter.RecruiterStatus.ACTIVE:
                    return "dashboard", "Your account is active", member
                elif member.status == Recruiter.RecruiterStatus.PENDING_SIGNUP:
                    if not member.address:
                        return "address_info", "hide agency fields", member
                    return SignupStep.DESCRIPTION.value, "Please complete description step", member

            except Recruiter.DoesNotExist:
                return SignupStep.BASIC_INFO.value, "Start your application", None

        elif user.is_client:
            try:
                member = ClientUserProfile.objects.get(user=user)
                if member.client.status == Client.Status.ACTIVE:
                    return "dashboard", "Welcome back", member
            except ClientUserProfile.DoesNotExist:
                return SignupStep.BASIC_INFO.value, "Start your application", None
