import requests

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import get_company_data, get_person_data  # Import the helper function


class ProxycurlPersonView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch person data from LinkedIn using Proxycurl API",
        manual_parameters=[
            openapi.Parameter(
                "linkedin_url",
                openapi.IN_QUERY,
                description="LinkedIn profile URL of the person",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: "Success - Returns person data",
            400: "Bad Request - Invalid or missing parameters",
        },
    )
    def get(self, request, *args, **kwargs):
        linkedin_url = request.query_params.get("linkedin_url")
        if not linkedin_url:
            return Response({"error": "linkedin_url parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person_data = get_person_data(linkedin_url)
            return Response(person_data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProxycurlCompanyView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch company data from LinkedIn using Proxycurl API",
        manual_parameters=[
            openapi.Parameter(
                "linkedin_url",
                openapi.IN_QUERY,
                description="LinkedIn profile URL of the company",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: "Success - Returns company data",
            400: "Bad Request - Invalid or missing parameters",
        },
    )
    def get(self, request, *args, **kwargs):
        linkedin_url = request.query_params.get("linkedin_url")
        if not linkedin_url:
            return Response({"error": "linkedin_url parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company_data = get_company_data(linkedin_url)
            return Response(company_data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
