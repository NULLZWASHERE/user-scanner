import re
from user_scanner.core.helpers import get_random_user_agent
from user_scanner.core.orchestrator import generic_validate
from user_scanner.core.result import Result

def validate_tiktok_email(email: str) -> Result:
    """TikTok Email Validation"""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return Result.error("Invalid email format")

    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Chrome OS"',
        "referer": "https://www.tiktok.com/",
        "origin": "https://www.tiktok.com",
    }

    url = "https://us.tiktok.com/passport/web/email/send_code/"

    body = (
        "mix_mode=1"
        f"&email={email.replace('@', '%40')}"
        "&type=31"
        "&aid=1459"
        "&is_sso=false"
        "&account_sdk_source=web"
        "&region=US"
        "&language=en"
        "&locale=en"
        "&did=7638008125426271757"
        "&email_logic_type=2"
        "&fixed_mix_mode=1"
    )

    def checker(response):
        try:
            data = response.json()
            if data.get("data") and data["data"].get("email_ticket"):
                return Result.taken()
            if data.get("message") == "success":
                return Result.taken()
            if data.get("status_code") in [10221, 11000, 11005]:
                return Result.available()
            return Result.taken()
        except:
            text = response.text.lower() if hasattr(response, 'text') else ""
            if '"email_ticket"' in text:
                return Result.taken()
            return Result.available()

    return generic_validate(
        url=url,
        func=checker,                    # ← This was missing
        show_url="https://www.tiktok.com/",
        headers=headers,
        data=body,
        method="POST",
        timeout=10.0
    )
