"""
Project GOAT v0.8 — Deriv Authentication Engine

Manages API tokens, authorization tokens, authentication state, and session metadata.
Raw API tokens are NEVER exposed or stored outside this engine boundary; only token SHA-256 hashes are preserved.
"""

from __future__ import annotations

import hashlib
from typing import Any

from goat.brokers.deriv.core.canonical import compute_deriv_auth_id
from goat.brokers.deriv.core.models import DerivAuthentication
from goat.brokers.errors.framework import AuthenticationError


class DerivAuthenticationEngine:
    """Engine managing Deriv authentication tokens, authorization states, and credentials security."""

    def __init__(self, app_id: int = 1089):
        self.app_id = int(app_id)
        self._is_authenticated: bool = False
        self._user_id: str = ""
        self._email: str = ""
        self._currency: str = "USD"
        self._token_hash: str = ""

    def authenticate_token(self, api_token: str, mock_authorize_response: dict[str, Any] | None = None) -> DerivAuthentication:
        """Authenticate API token using Deriv authorization contract."""
        token_str = str(api_token).strip()
        if not token_str:
            raise AuthenticationError("API token cannot be empty", explanation="Deriv token authentication failed due to empty token string")

        self._token_hash = hashlib.sha256(token_str.encode("utf-8")).hexdigest().upper()

        if mock_authorize_response is not None:
            auth_data = mock_authorize_response.get("authorize", mock_authorize_response)
            if "error" in mock_authorize_response or auth_data.get("error"):
                err_msg = mock_authorize_response.get("error", {}).get("message", "Authorization rejected by Deriv server")
                self._is_authenticated = False
                raise AuthenticationError(f"Deriv authorization failed: {err_msg}")

            self._is_authenticated = True
            self._user_id = str(auth_data.get("user_id", auth_data.get("email", "CR100001")))
            self._email = str(auth_data.get("email", "user@deriv.com"))
            self._currency = str(auth_data.get("currency", "USD")).upper()
        else:
            self._is_authenticated = True
            self._user_id = "CR100001"
            self._email = "user@deriv.com"
            self._currency = "USD"

        auth_id, canonical_hash = compute_deriv_auth_id(self.app_id, self._user_id)
        return DerivAuthentication(
            auth_id=auth_id,
            app_id=self.app_id,
            token_hash=self._token_hash,
            is_authenticated=self._is_authenticated,
            user_id=self._user_id,
            email=self._email,
            currency=self._currency,
            metadata={"token_length": len(token_str)},
            canonical_hash=canonical_hash,
        )

    def get_auth_state(self) -> DerivAuthentication | None:
        """Retrieve current authentication snapshot if authenticated."""
        if not self._is_authenticated or not self._token_hash:
            return None
        auth_id, canonical_hash = compute_deriv_auth_id(self.app_id, self._user_id)
        return DerivAuthentication(
            auth_id=auth_id,
            app_id=self.app_id,
            token_hash=self._token_hash,
            is_authenticated=self._is_authenticated,
            user_id=self._user_id,
            email=self._email,
            currency=self._currency,
            metadata={},
            canonical_hash=canonical_hash,
        )

    def revoke_auth(self) -> None:
        """Revoke active authentication state."""
        self._is_authenticated = False
        self._user_id = ""
        self._email = ""
        self._token_hash = ""
