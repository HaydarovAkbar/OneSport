from rest_framework import permissions

from grid.clients.models import ClientUserProfile


class CanSendTeamInvite(permissions.BasePermission):
    message = "You don't have permission to send team invites."

    def has_permission(self, request, view):
        user = request.user

        if user.is_client:
            return (
                hasattr(user, "clientuserprofile")
                and user.clientuserprofile.user_type == ClientUserProfile.UserType.SUPERUSER
            )
        elif user.is_recruiter:
            return hasattr(user, "recruiter") and user.recruiter.superuser

        return False


class IsTeamMember(permissions.BasePermission):
    """
    Allows access only to team members.
    """

    message = "user is not a team member"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_team_member)
