"""
Project GOAT v0.8 — Test Suite: Deriv Authentication Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.deriv.auth.engine import DerivAuthenticationEngine
from goat.brokers.errors.framework import AuthenticationError

APP_IDS = [1089, 9999, 12345]
TOKENS = ["token_abc123", "token_xyz987", "secret_token_111"]
USERS = ["CR100001", "CR200002", "CR300003"]
CURRENCIES = ["USD", "EUR", "GBP", "AUD"]


@pytest.mark.parametrize("app_id,token,user_id", [(a, t, u) for a in APP_IDS for t in TOKENS for u in USERS])
def test_deriv_auth_engine_matrix(app_id, token, user_id):
    engine = DerivAuthenticationEngine(app_id=app_id)
    assert engine.get_auth_state() is None

    mock_response = {
        "authorize": {
            "email": f"{user_id}@deriv.com",
            "user_id": user_id,
            "currency": "USD",
        }
    }
    auth = engine.authenticate_token(token, mock_authorize_response=mock_response)
    assert auth.auth_id.startswith("DAT_")
    assert auth.app_id == app_id
    assert auth.is_authenticated is True
    assert auth.user_id == user_id
    assert auth.token_hash != token

    current = engine.get_auth_state()
    assert current is not None
    assert current.auth_id == auth.auth_id

    engine.revoke_auth()
    assert engine.get_auth_state() is None


@pytest.mark.parametrize("currency,user_id", [(c, u) for c in CURRENCIES for u in USERS])
def test_deriv_auth_engine_currencies_matrix(currency, user_id):
    engine = DerivAuthenticationEngine(app_id=1089)
    mock_response = {
        "authorize": {
            "email": f"{user_id}@deriv.com",
            "user_id": user_id,
            "currency": currency,
        }
    }
    auth = engine.authenticate_token("valid_token_string", mock_authorize_response=mock_response)
    assert auth.currency == currency
    assert auth.user_id == user_id


def test_deriv_auth_engine_empty_token_failure():
    engine = DerivAuthenticationEngine()
    with pytest.raises(AuthenticationError):
        engine.authenticate_token("  ")


def test_deriv_auth_engine_rejected_token():
    engine = DerivAuthenticationEngine()
    rejected_response = {"error": {"message": "Invalid token"}}
    with pytest.raises(AuthenticationError):
        engine.authenticate_token("invalid_token", mock_authorize_response=rejected_response)
