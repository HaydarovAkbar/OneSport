from rest_framework.permissions import BasePermission

from grid.admins.models import AdminUserProfile
from grid.clients.models import ClientUserProfile
from grid.recruiters.models import Recruiter
from grid.users.choices import Roles


class IsRecruiter(BasePermission):
    message = "User must be a recruiter to access this resource."

    def has_permission(self, request, view):
        return request.user.role == Roles.RECRUITER


class IsClient(BasePermission):
    message = "User must be a client to access this resource."

    def has_permission(self, request, view):
        return request.user.role == Roles.CLIENT


class IsAdmin(BasePermission):
    message = "User must be a admin to access this resource."

    def has_permission(self, request, view):
        return request.user.role == Roles.ADMIN


# Permissions for Subroles


class IsRecruiterSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return Recruiter.objects.filter(user=request.user, superuser=True).exists()


class IsRecruiterMember(BasePermission):
    def has_permission(self, request, view):
        return Recruiter.objects.filter(user=request.user, superuser=False).exists()


class IsClientSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return ClientUserProfile.objects.filter(
            user=request.user, user_type=ClientUserProfile.UserType.SUPERUSER
        ).exists()


class IsClientAdmin(BasePermission):
    def has_permission(self, request, view):
        return ClientUserProfile.objects.filter(user=request.user, user_type=ClientUserProfile.UserType.ADMIN).exists()


class IsAdminSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(
            user=request.user, user_type=AdminUserProfile.UserType.SUPERADMIN
        ).exists()


class IsAdminAdmin(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(user=request.user, user_type=AdminUserProfile.UserType.ADMIN).exists()


class IsAdminEditor(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(user=request.user, user_type=AdminUserProfile.UserType.EDITOR).exists()


class IsAdminViewer(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(user=request.user, user_type=AdminUserProfile.UserType.VIEWER).exists()


class IsAdminAccountant(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(
            user=request.user, user_type=AdminUserProfile.UserType.ACCOUNTANT
        ).exists()


class IsAdminMember(BasePermission):
    def has_permission(self, request, view):
        return AdminUserProfile.objects.filter(user=request.user, user_type=AdminUserProfile.UserType.MEMBER).exists()


# class IsUserBelongsToClient (BasePermission):
# class IsUserBelongsToAgency (BasePermission):
