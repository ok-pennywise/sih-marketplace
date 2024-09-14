from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional, Type, TypeVar
from uuid import uuid4

from core.settings import SECRET_KEY
from model_utils import aware_utcnow, datetime_from_epoch, datetime_to_epoch

import json
from collections.abc import Iterable
from datetime import timedelta
from typing import Any, Optional, Type, Union
import jwt
from jwt import algorithms


try:
    from jwt import PyJWKClient, PyJWKClientError

    JWK_CLIENT_AVAILABLE = True
except ImportError:
    JWK_CLIENT_AVAILABLE = False

ALLOWED_ALGORITHMS = {
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
}


class TokenBuilderError(Exception): ...


class TokenError(Exception): ...


class TokenBuilder:
    def __init__(
        self,
        algorithm: str,
        signing_key: Optional[str] = None,
        verifying_key: str = "",
        audience: Union[str, Iterable, None] = None,
        issuer: Optional[str] = None,
        jwk_url: Optional[str] = None,
        leeway: Union[float, int, timedelta, None] = None,
        json_encoder: Optional[Type[json.JSONEncoder]] = None,
    ) -> None:
        self._validate_algorithm(algorithm)

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        self.audience = audience
        self.issuer = issuer

        if JWK_CLIENT_AVAILABLE:
            self.jwks_client = PyJWKClient(jwk_url) if jwk_url else None
        else:
            self.jwks_client = None

        self.leeway = leeway
        self.json_encoder = json_encoder

    @staticmethod
    def _validate_algorithm(algorithm: str) -> None:
        """
        Ensure that the nominated algorithm is recognized, and that cryptography is installed for those
        algorithms that require it
        """
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBuilderError(f"Unrecognized algorithm type '{algorithm}'")

        if algorithm in algorithms.requires_cryptography and not algorithms.has_crypto:
            raise TokenBuilderError(
                f"You must have cryptography installed to use {algorithm}."
            )

    def get_leeway(self) -> timedelta:
        if self.leeway is None:
            return timedelta(seconds=0)
        elif isinstance(self.leeway, (int, float)):
            return timedelta(seconds=self.leeway)
        elif isinstance(self.leeway, timedelta):
            return self.leeway
        else:
            raise TokenBuilderError(
                f"Unrecognized type '{type(self.leeway)}', 'leeway' must be of type int, float or timedelta."
            )

    def get_verifying_key(self, key) -> Optional[str]:
        if self.algorithm.startswith("HS"):
            return self.signing_key

        if self.jwks_client:
            try:
                return self.jwks_client.get_signing_key_from_jwt(key).key
            except PyJWKClientError as ex:
                raise TokenBuilderError("Key is invalid or expired") from ex

        return self.verifying_key

    def encode(self, payload: dict[str, Any]) -> str:
        """
        Returns an encoded key for the given payload dictionary.
        """
        payload_ = payload.copy()
        if self.audience:
            payload_["aud"] = self.audience
        if self.issuer:
            payload_["iss"] = self.issuer

        return jwt.encode(
            payload_,
            self.signing_key,
            algorithm=self.algorithm,
            json_encoder=self.json_encoder,
        )

    def decode(
        self, key: str, verify_signature: bool = True, verify_expiry: bool = True
    ) -> dict[str, Any]:
        """
        Performs a validation of the given key and returns its payload
        dictionary.

        Raises a `keyBackendError` if the key is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return jwt.decode(
                key,
                self.get_verifying_key(key),
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.get_leeway(),
                options={
                    "verify_aud": self.audience is not None,
                    "verify_signature": verify_signature,
                    "verify_expiry": verify_expiry,
                },
            )
        except jwt.exceptions.InvalidTokenError:
            raise TokenBuilderError("Key is invalid or expired")


T = TypeVar("T", bound="Token")


def tracked(cls_: Type[T]) -> Type[T]:
    class Wrapper(cls_):

        @classmethod
        def issue(cls, **kw):
            Wrapper.__name__ = cls_.__name__
            key = cls_.issue(**kw)
            return key

    return Wrapper


class TokenKeyClaims:
    KEY_TYPE: str = "kty"
    KEY_ID: str = "kid"
    EXP: str = "exp"
    IAT: str = "iat"


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """

    lifetime: Optional[timedelta] = None
    no_copy_claims: Optional[list[str]] = []

    def __init__(
        self,
        key: Optional[str] = None,
        verify_signature: bool = True,
        verify_expiry: bool = True,
    ) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given key is invalid, expired, or otherwise not safe
        to use.
        """
        if not self.lifetime:
            raise TokenError("Cannot create key with no lifetime")

        self.key = key
        self.current_time = aware_utcnow()

        # Set up key
        if key:
            # An encoded key was provided
            # Decode key
            try:
                self.payload = self.builder().decode(
                    key, verify_signature=verify_signature, verify_expiry=verify_expiry
                )
            except TokenBuilderError:
                raise TokenError("Key is invalid or expired")

            if verify_signature:
                self.verify()
        else:
            # New key.  Skip all the verification steps.
            self.payload = {TokenKeyClaims.KEY_TYPE: self.key_type}

            # Set "exp" and "iat" claims with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
            self.set_iat(at_time=self.current_time)

            # Set "jti" claim
            self.set_kid()

    def __repr__(self) -> str:
        return repr(self.payload)

    def __getitem__(self, key: str):
        return self.payload[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.payload[key] = value

    def __delitem__(self, key: str) -> None:
        del self.payload[key]

    def __contains__(self, key: str) -> Any:
        return key in self.payload

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.payload.get(key, default)

    def __str__(self) -> str:
        """
        Signs and returns a key as a base64 encoded string.
        """
        return self.builder().encode(self.payload)

    def verify(self) -> None:
        """
        Performs additional validation steps which were not performed when this
        key was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization keys, we require an "exp"
        # claim.  We don't want any zombie keys walking around.
        self.check_exp()

        # If the defaults are not None then we should enforce the
        # requirement of these settings.As above, the spec labels
        # these as optional.
        self.verify_key_type()

    def verify_key_type(self) -> None:
        """
        Ensures that the key type claim is present and has the correct value.
        """
        try:
            key_type = self.payload[TokenKeyClaims.KEY_TYPE]
            if self.key_type != key_type:
                raise TokenError("key has wrong type")
        except KeyError:
            raise TokenError("key has no type")

    def set_kid(self) -> None:
        """
        Populates the configured jti claim of a key with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self.payload[TokenKeyClaims.KEY_ID] = uuid4().time

    def set_exp(
        self,
        from_time: Optional[datetime] = None,
        lifetime: Optional[timedelta] = None,
    ) -> None:
        """
        Updates the expiration time of a key.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.4
        """
        if from_time is None:
            from_time = self.current_time

        if not lifetime:
            lifetime = self.lifetime

        self.payload[TokenKeyClaims.EXP] = datetime_to_epoch(from_time + lifetime)

    def set_iat(self, at_time: Optional[datetime] = None) -> None:
        """
        Updates the time at which the key was issued.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.6
        """
        if at_time is None:
            at_time = self.current_time

        self.payload[TokenKeyClaims.IAT] = datetime_to_epoch(at_time)

    @property
    def kid(self) -> str:
        return self.payload[TokenKeyClaims.KEY_ID]

    @property
    def key_type(self) -> str:
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in self.__class__.__name__]
        ).lstrip("_")

    @property
    def iat(self) -> datetime:
        return datetime_from_epoch(self.payload[TokenKeyClaims.IAT])

    @property
    def exp(self) -> datetime:
        return datetime_from_epoch(self.payload[TokenKeyClaims.EXP])

    def check_exp(self, current_time: Optional[datetime] = None) -> None:
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[TokenKeyClaims.EXP]
        except KeyError:
            raise TokenError(f"Key has no '{TokenKeyClaims.EXP}' claim")

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.builder().get_leeway()
        if claim_time <= current_time - leeway:
            raise TokenError("Key has expired")

    @classmethod
    def issue(cls: Type[T], **kw) -> T:
        key = cls()

        for k, v in kw.items():
            key[k] = v

        return key

    def builder(self) -> TokenBuilder:
        return TokenBuilder(
            algorithm="HS256",
            signing_key=SECRET_KEY,
        )


class RefreshToken(Token):
    lifetime = timedelta(days=7)

    no_copy_claims = [
        TokenKeyClaims.EXP,
        TokenKeyClaims.KEY_TYPE,
        TokenKeyClaims.KEY_ID,
    ]


class AccessToken(Token):
    lifetime = timedelta(minutes=10)

    @property
    def refresh_token(self) -> RefreshToken:
        key = RefreshToken.issue()
        for k, v in self.payload.items():
            if k not in key.no_copy_claims:
                key[k] = v
        return key
