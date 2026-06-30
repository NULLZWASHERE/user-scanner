import re
import json
from user_scanner.core.helpers import get_random_user_agent
from user_scanner.core.orchestrator import generic_validate
from user_scanner.core.result import Result

def validate_microsoft_email(email: str) -> Result:
    """Improved Microsoft / Outlook Email Checker"""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return Result.error("Invalid email format")

    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Chrome OS"',
        "referer": "https://login.microsoftonline.com/",
    }

    url = "https://login.microsoftonline.com/common/GetCredentialType?mkt=en-US"

    payload = {
        "username": email,
        "isOtherIdpSupported": True,
        "checkPhones": False,
        "isRemoteNGCSupported": True,
        "isCookieBannerShown": False,
        "isFidoSupported": True,
        "originalRequest": "",
        "country": "US",
        "forceotclogin": False,
        "isExternalFederationDisallowed": False,
        "isRemoteConnectSupported": False,
        "federationFlags": 0,
        "isSignup": False,
        "flowToken": "",
        "isAccessPassSupported": True
    }

    def process(response):
        try:
            data = response.json()
            
            if_exists = data.get("IfExistsResult")

            if if_exists == 1:
                return Result.taken()      # Real account
            elif if_exists == 0:
                return Result.available()  # Does not exist

            # Extra safety check
            if data.get("Credentials", {}).get("HasPassword") is True:
                return Result.taken()

            return Result.available()

        except Exception as e:
            # Fallback
            text = response.text.lower()
            if '"ifexistsresult":1' in text or '"haspassword":true' in text:
                return Result.taken()
            return Result.available()

    return generic_validate(
        url=url,
        func=process,
        show_url="https://account.microsoft.com/",
        headers=headers,
        data=json.dumps(payload),
        method="POST",
        timeout=8.0
    )
