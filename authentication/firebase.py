import os
import sys
from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials

# Determine if we're running in a test environment
is_testing = "pytest" in sys.modules

# Get the project root directory for reliable file paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Determine which credentials file to use based on environment
if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith(".production"):
    cred_path = BASE_DIR / ".envs" / ".production" / "firebase.json"
else:
    cred_path = BASE_DIR / ".envs" / ".local" / "firebase.json"

# Handle Firebase initialization with proper test environment support
if is_testing:
    # For tests, try to use credentials if available, otherwise skip initialization
    try:
        if cred_path.exists():
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
    except Exception:  # noqa: BLE001, S110
        # Silently skip Firebase initialization in test environment
        pass
else:
    # In non-test environments, credentials must exist
    if not cred_path.exists():
        msg = f"Firebase credentials not found at {cred_path}"
        raise FileNotFoundError(msg)

    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)


def validate_token(token: str) -> None:
    """
    Validate and decode a Firebase authentication token.
    This function verifies the validity of a Firebase ID token and returns the decoded payload.
    Args:
        token (str): The Firebase ID token to validate.
    Returns:
        dict: The decoded token payload containing user information like UID, email, etc.
    Raises:
        Exception: If the token is invalid or verification fails.
    """  # noqa: E501

    try:
        data = auth.verify_id_token(token)
    except Exception as e:
        msg = "Invalid token"
        raise Exception(msg) from e  # noqa: TRY002

    return data


def get_user_info(token):
    """
    Retrieves user information from a Firebase authentication token.

    This function verifies the provided token, extracts the user ID (uid),
    fetches the user information from Firebase, and formats the user's details.

    Args:
        token (str): The Firebase authentication token to verify.

    Returns:
        dict: A dictionary containing the user's information with the following keys:
            - uid (str): The user's unique identifier.
            - email (str): The user's email address.
            - first_name (str): The user's first name extracted from display_name.
            - last_name (str): The user's last name extracted from display_name.
            - photo_url (str): The URL to the user's profile photo.

    Raises:
        FirebaseError: If the token is invalid or there's an issue with Firebase authentication.
    """  # noqa: E501

    decoded_token = auth.verify_id_token(token)
    uid = decoded_token["uid"]
    user = auth.get_user(uid)

    first_name = user.display_name.split(" ")[0] if user.display_name else "None"
    last_name = user.display_name.split(" ")[-1] if len(user.display_name.split(" ")) > 1 else ""

    return {
        "uid": user.uid,
        "email": user.email,
        "first_name": first_name,
        "last_name": last_name,
        "photo_url": user.photo_url,
    }
