import json
from typing import Literal

import requests
import tenacity
from django.db import models
from tenacity import stop_after_attempt, stop_after_delay


class BaseTelegramUserModel(models.Model):
    class Meta:
        abstract = True

    BOT_TOKEN = None

    user_id = models.CharField(max_length=25, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, default="")
    username = models.CharField(max_length=255, blank=True, default="")

    is_active = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @tenacity.retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
    def send_chat_action(self, action: Literal["typing"]) -> bool:
        url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendChatAction"
        payload = json.dumps({"chat_id": self.user_id, "action": action})
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.ok

    @tenacity.retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
    def send_message(self, message: str) -> bool:
        self.send_chat_action("typing")

        url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": self.user_id, "text": message, "parse_mode": "HTML"})
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.ok

    def send_document(self, document, caption="") -> bool:
        self.send_chat_action("upload_document")

        url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendDocument"
        payload = json.dumps({"chat_id": self.user_id, "document": document, "caption": caption, "parse_mode": "HTML"})
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.ok
