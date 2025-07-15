import re

import phonenumbers

from django.core.validators import URLValidator
from rest_framework import serializers


ALLOWED_COUNTRIES = {
    "NZ": "New Zealand",
    "AU": "Australia",
    "CA": "Canada",
    "GB": "United Kingdom",
    "US": "United States",
}


def validate_linkedin_profile_url(url):
    """Validates that URL is a LinkedIn profile URL"""
    url_validator = URLValidator()
    try:
        url_validator(url)

        # Check if it's a LinkedIn profile URL
        pattern = r"^https?:\/\/(?:www\.)?linkedin\.com\/in\/[\w\-\_]+\/?$"
        if not re.match(pattern, url):
            raise serializers.ValidationError(
                "Invalid LinkedIn profile URL. It should look like: https://www.linkedin.com/in/username"
            )
    except Exception as e:
        print("Exception: ", e)
        raise serializers.ValidationError("Invalid URL format")

    return url


def validate_phone_number(phone, region):
    """Validates and formats phone number for allowed countries"""
    if not phone:
        return None

    # Remove any non-numeric characters except + for initial parsing
    cleaned = re.sub(r"[^\d+]", "", phone)
    print("Cleaned Number:", cleaned)

    try:
        number = phonenumbers.parse(cleaned, region)

        # Check if country is allowed
        region = phonenumbers.region_code_for_number(number)
        if region not in ALLOWED_COUNTRIES:
            raise serializers.ValidationError(
                f"Phone number must be from one of: {', '.join(ALLOWED_COUNTRIES.values())}"
            )

        if not phonenumbers.is_valid_number(number):
            raise serializers.ValidationError("Invalid phone number format")

        # Format to E.164 format
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    except phonenumbers.NumberParseException:
        # traceback.print_exc()
        raise serializers.ValidationError("Unable to parse phone number")
