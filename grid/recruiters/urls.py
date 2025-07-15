from django.urls import include, path
from rest_framework.routers import DefaultRouter

from grid.recruiters.views import (  # MemberRecruiterSignupView,
    AgencyViewSet,
    BankAccountViewSet,
    JobCategoryListView,
    RecruiterSignupViewSet,
    RecruiterViewSet,
)


router = DefaultRouter()
router.register(r"recruiters", RecruiterViewSet, basename="recruiter")
router.register(r"agencies", AgencyViewSet, basename="agency")
router.register(r"signup", RecruiterSignupViewSet, basename="recruiter-profile-signup")
router.register(r"bank-accounts", BankAccountViewSet, basename="bankaccount")


urlpatterns = [
    path("", include(router.urls)),
    path("job-categories/", JobCategoryListView.as_view(), name="job-category-list"),
    # path("member-signup/", MemberRecruiterSignupView.as_view(), name='member-recruiter-signup'),
]
