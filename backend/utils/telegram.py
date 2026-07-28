import hashlib
import hmac
import json
from typing import TypedDict
from urllib.parse import unquote

from django.http import HttpRequest


class TelegramMiniAppData(TypedDict):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str


class TelegramUser(TypedDict):
    id: int
    first_name: str
    last_name: str = ""
    username: str = ""


class TelegramWebhookParser:
    def __init__(self, request_data: HttpRequest):
        self.request_data = request_data

    @property
    def data(self) -> dict | None:
        try:
            data = json.loads(self.request_data)
        except Exception:
            return None

        # Reject if not first message (eg. edited or deleted message)
        if not data.get("message"):
            return None

        # Reject if messaage is not text message
        if data.get("message") and not data.get("message").get("text"):
            return None

        user = data.get("message").get("from")
        message = data.get("message").get("text", "")

        return {"user": user, "text_message": message}

    def get_user(self) -> TelegramUser:
        required_keys = ["first_name", "id"]

        try:
            payload = json.loads(self.request_data)
        except Exception:
            raise Exception("Failed to parse JSON payload ☠️")

        message = payload.get("message", None)
        edited_message = payload.get("edited_message", None)

        if not message and not edited_message:
            raise Exception("Unable to find `message` and `edited_message` data 😿")

        user_data = message.get("from") or edited_message.get("from")

        for key in required_keys:
            if not user_data.get(key):
                raise Exception(f"Unable to get the user information because `{key}` is missing 😾")

        return {
            "id": user_data.get("id"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name", ""),
            "username": user_data.get("username", ""),
        }

    def get_text_message(self) -> str:
        try:
            payload = json.loads(self.request_data)
        except Exception:
            raise Exception("Failed to parse JSON payload ☠️")

        message = payload.get("message", None)

        if not message:
            raise Exception("Message is not available 😿")

        text = message.get("text")
        return text


def validate_telegram_mini_app_data(
    query_string: str, bot_token: str, constant_str: str = "WebAppData"
) -> TelegramMiniAppData:
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    query_string - the query string passed by the web app
    bot_token - Telegram bot's token
    constant_str - constant string (default = "WebAppData")
    """

    # Parse the query string and extract the hash string
    parsed_data = dict(chunk.split("=") for chunk in unquote(query_string).split("&"))
    received_hash = parsed_data.pop("hash")

    # Sort the remaining parsed data
    sorted_data = sorted(parsed_data.items(), key=lambda x: x[0])
    data_string = "\n".join([f"{key}={value}" for key, value in sorted_data])

    # Generate the secret key using the constant string and bot token
    secret_key = hmac.new(constant_str.encode(), bot_token.encode(), hashlib.sha256).digest()

    # Generate the data check hash using the secret key and sorted data string
    calculated_hash = hmac.new(secret_key, data_string.encode(), hashlib.sha256).hexdigest()

    # Validate the received hash with the calculated hash
    if not calculated_hash == received_hash:
        raise Exception(
            f"The given data hash is not valid! Received hash: {received_hash}, Calculated hash: {calculated_hash}"
        )

    user_data = json.loads(parsed_data["user"])
    data: TelegramMiniAppData = {
        "id": int(user_data["id"]),
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "username": user_data["username"],
        "language_code": user_data["language_code"] or "en",
    }

    return data
