from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID"

def verify_google_token(token):

    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return {
            "email": info["email"],
            "name": info.get("name")
        }

    except Exception:
        return None