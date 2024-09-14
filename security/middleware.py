from typing import Any

from django.http import HttpResponse

from security.keys import TokenError, AccessToken


class ClaimAssociationMiddleware:
    openapi_scheme: str = "bearer"
    header: str = "Authorization"

    claims: set[str] = {"user_id", "user_type"}

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        headers = request.headers
        params = headers.get(self.header)
        if params:
            parts = params.split(" ")
            if parts[0].lower() == self.openapi_scheme:
                try:
                    payload: dict[str, Any] = AccessToken(
                        key=parts[1], verify_expiry=False
                    ).payload
                    for i in self.claims:
                        setattr(request, i, payload.get(i, None))
                except TokenError as e:
                    print(e)
                    for i in self.claims:
                        setattr(request, i, None)
        else:
            for i in self.claims:
                setattr(request, i, None)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response
