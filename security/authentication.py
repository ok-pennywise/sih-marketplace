from typing import Optional, Any, Type

from django.http import HttpRequest
from ninja.security import HttpBearer

from security.keys import AccessToken, TokenError, T
from users.models import User


class _HttpBearer(HttpBearer):
    token_class: Type[T] = None
    user_type: str = ""

    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        if not self.token_class:
            raise AttributeError("Must add the key class")
        try:
            payload = self.token_class(key=token).payload
            user_type = payload["user_type"]
            if self.user_type == "":
                return payload
            elif user_type != self.user_type:
                return None
            return payload
        except (KeyError, TokenError):
            return None


class FarmerAccessAuthorization(_HttpBearer):
    token_class = AccessToken
    user_type = User.FARMER


class BuyerAccessAuthorization(_HttpBearer):
    token_class = AccessToken
    user_type = User.BUYER


class GeneralAccessAuthorization(_HttpBearer):
    token_class = AccessToken
    user_type = ""
