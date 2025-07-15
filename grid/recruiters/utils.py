from datetime import datetime
from typing import Dict, Optional

import requests

from django.core.files.base import ContentFile

from grid.clients.models import Address
from grid.core.helpers import get_person_data
from grid.recruiters.models import Agency, JobCategory, Recruiter


def create_recruiter_from_basic_info(user, profile_photo, basic_info_data):
    """Creates a recruiter object with basic information"""
    # Extract industry data
    primary_industry_uuid = basic_info_data.pop("primary_industry", None)
    secondary_industry_uuid = basic_info_data.pop("sec_industry", None)

    # Get job category instances
    primary_industry = JobCategory.objects.filter(uuid=primary_industry_uuid).first() if primary_industry_uuid else None
    secondary_industry = (
        JobCategory.objects.filter(uuid=secondary_industry_uuid).first() if secondary_industry_uuid else None
    )
    is_superuser = True if not user.is_team_member else False
    recruiter_data = {
        "first_name": basic_info_data["first_name"],
        "last_name": basic_info_data["last_name"],
        "phone": basic_info_data.get("phone"),
        "linkedin": basic_info_data["linkedin"],
        "primary_industry": primary_industry,
        "sec_industry": secondary_industry,
        "profile_photo": profile_photo,
        "superuser": is_superuser,
    }

    recruiter = Recruiter(user=user, **recruiter_data)
    if user.is_team_member:
        recruiter.agency = user.owner_profile.agency
        recruiter.approval_date = datetime.now()
    recruiter.save()

    return recruiter


def create_agency_and_address_from_info(agency_info_data, user):
    """Creates agency with provided information"""
    address_data = agency_info_data.pop("address", None)

    agency = Agency.objects.create(
        agency_name=agency_info_data.get("agency_name"),
        make_payable_to=agency_info_data["make_payable_to"],
        is_individual=agency_info_data["is_individual"],
        website=agency_info_data.pop("website", None),
        linkedin=agency_info_data.pop("linkedin", None),
    )
    if address_data:
        address = Address.objects.create(**address_data, by_user=user)
        return agency, address

    return agency, None


def download_image(url: str):
    """Downloads image"""
    if not url:
        print("No picture in linkedin data")
        return None
    print("Picture found in linkedin data, downloading it ...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Get file extension from content type
            content_type = response.headers.get("content-type", "")
            ext = {
                "image/jpeg": "jpg",
                "image/png": "png",
            }.get(content_type, "jpg")

            return ContentFile(response.content, name=f"profile_photo.{ext}")
    except Exception as e:
        print(f"Error downloading profile image: {str(e)}")
    return None


def extract_linkedin_data(data: dict) -> dict:
    """Extracts relevant fields from LinkedIn API response"""

    profile_pic_url = data.get("profile_pic_url")
    return {
        "profile_pic_url": profile_pic_url,
        "profile_photo": download_image(profile_pic_url) if profile_pic_url else None,
        "headline": data.get("headline"),
        "summary": data.get("summary"),
        "country": data.get("country"),
        "country_full_name": data.get("country_full_name"),
        "state": data.get("state"),
    }


def process_person_linkedin_data(linkedin_url: str):
    """Process LinkedIn data synchronously"""
    try:
        # Get LinkedIn data
        linkedin_data = get_person_data(linkedin_url)

        if not linkedin_data:
            return None

        # Extract relevant fields
        extracted_data = extract_linkedin_data(linkedin_data)

        return extracted_data

    except Exception as e:
        print(f"Error processing LinkedIn data: {str(e)}")
        return None
