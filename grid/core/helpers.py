import requests

from django.conf import settings  # Import settings to access the API key


def get_person_data(linkedin_url):
    url = "https://nubela.co/proxycurl/api/v2/linkedin"
    headers = {"Authorization": f"Bearer {settings.PROXYCURL_API_KEY}"}
    params = {"linkedin_profile_url": linkedin_url}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_company_data(linkedin_url):
    url = "https://nubela.co/proxycurl/api/linkedin/company"
    headers = {"Authorization": f"Bearer {settings.PROXYCURL_API_KEY}"}
    params = {
        "url": linkedin_url,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
