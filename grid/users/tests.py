from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from grid.users.choices import InviteStatus, InviteType, Roles
from grid.users.models import TeamInvite, User


User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.role, Roles.CLIENT)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, Roles.CLIENT)

    def test_email_required(self):
        """Test that email is required"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_email_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_user_role_properties(self):
        """Test user role properties"""
        # Test client role
        client_user = User.objects.create_user(email="client@example.com", password="pass123", role=Roles.CLIENT)
        self.assertTrue(client_user.is_client)
        self.assertFalse(client_user.is_recruiter)
        self.assertFalse(client_user.is_admin)

        # Test recruiter role
        recruiter_user = User.objects.create_user(
            email="recruiter@example.com", password="pass123", role=Roles.RECRUITER
        )
        self.assertFalse(recruiter_user.is_client)
        self.assertTrue(recruiter_user.is_recruiter)
        self.assertFalse(recruiter_user.is_admin)

        # Test admin role
        admin_user = User.objects.create_user(email="admin@example.com", password="pass123", role=Roles.ADMIN)
        self.assertFalse(admin_user.is_client)
        self.assertFalse(admin_user.is_recruiter)
        self.assertTrue(admin_user.is_admin)


class TeamInviteModelTests(TestCase):
    """Test cases for TeamInvite model"""

    def setUp(self):
        self.inviter = User.objects.create_user(email="inviter@example.com", password="pass123", role=Roles.CLIENT)
        self.invite_data = {
            "email": "invited@example.com",
            "inviter": self.inviter,
            "invite_type": InviteType.CLIENT,
            "status": InviteStatus.PENDING,
        }

    def test_create_team_invite(self):
        """Test creating a team invite"""
        invite = TeamInvite.objects.create(**self.invite_data)
        self.assertEqual(invite.email, self.invite_data["email"])
        self.assertEqual(invite.inviter, self.inviter)
        self.assertEqual(invite.invite_type, InviteType.CLIENT)
        self.assertEqual(invite.status, InviteStatus.PENDING)
        self.assertIsNotNone(invite.token)

    def test_token_auto_generation(self):
        """Test that token is automatically generated"""
        invite = TeamInvite.objects.create(**self.invite_data)
        self.assertIsNotNone(invite.token)
        self.assertTrue(len(invite.token) > 0)

    def test_token_unique(self):
        """Test that tokens are unique"""
        invite1 = TeamInvite.objects.create(**self.invite_data)
        invite2 = TeamInvite.objects.create(
            email="another@example.com", inviter=self.inviter, invite_type=InviteType.CLIENT
        )
        self.assertNotEqual(invite1.token, invite2.token)

    def test_user_team_invite_property(self):
        """Test user's team_invite property"""
        # Create and accept an invite
        invite = TeamInvite.objects.create(**self.invite_data)
        invite.status = InviteStatus.ACCEPTED
        invite.save()

        # Create user with the invited email
        user = User.objects.create_user(email="invited@example.com", password="pass123")

        # Test team_invite property
        self.assertEqual(user.team_invite, invite)

    def test_user_is_team_member_property(self):
        """Test user's is_team_member property"""
        # Create user without invite
        user = User.objects.create_user(email="regular@example.com", password="pass123")
        self.assertFalse(user.is_team_member)

        # Create and accept an invite
        invite = TeamInvite.objects.create(
            email="regular@example.com",
            inviter=self.inviter,
            invite_type=InviteType.CLIENT,
            status=InviteStatus.ACCEPTED,
        )
        self.assertTrue(user.is_team_member)


class UserAPITests(APITestCase):
    """Test cases for User API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123", role=Roles.CLIENT)
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """Test retrieving user profile"""
        url = "/api/auth/user/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_user_profile(self):
        """Test updating user profile"""
        url = "/api/auth/user/"
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_authentication_required(self):
        """Test that authentication is required"""
        self.client.logout()
        url = "/api/auth/user/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationTests(APITestCase):
    """Test cases for authentication endpoints"""

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_registration(self):
        """Test user registration"""
        url = "/api/auth/registration/"
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_user_login(self):
        """Test user login"""
        # Create user first
        User.objects.create_user(**self.user_data)

        url = "/api/auth/login/"
        login_data = {"email": self.user_data["email"], "password": self.user_data["password"]}
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        url = "/api/auth/login/"
        login_data = {"email": "invalid@example.com", "password": "wrongpassword"}
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        """Test token refresh"""
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)

        url = "/api/auth/token/refresh/"
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout(self):
        """Test user logout"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)

        url = "/api/auth/logout/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamInviteTests(APITestCase):
    """Test cases for team invite functionality"""

    def setUp(self):
        self.inviter = User.objects.create_user(email="inviter@example.com", password="pass123", role=Roles.CLIENT)
        self.client.force_authenticate(user=self.inviter)

    def test_send_team_invite(self):
        """Test sending team invite"""
        url = "/api/team/invite/"
        data = {"email": "invited@example.com", "invite_type": InviteType.CLIENT}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamInvite.objects.filter(email=data["email"]).exists())

    def test_accept_team_invite(self):
        """Test accepting team invite"""
        # Create invite
        invite = TeamInvite.objects.create(
            email="invited@example.com", inviter=self.inviter, invite_type=InviteType.CLIENT
        )

        url = f"/api/team/invite/{invite.token}/accept/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invite.refresh_from_db()
        self.assertEqual(invite.status, InviteStatus.ACCEPTED)

    def test_decline_team_invite(self):
        """Test declining team invite"""
        # Create invite
        invite = TeamInvite.objects.create(
            email="invited@example.com", inviter=self.inviter, invite_type=InviteType.CLIENT
        )

        url = f"/api/team/invite/{invite.token}/decline/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invite.refresh_from_db()
        self.assertEqual(invite.status, InviteStatus.DECLINED)
