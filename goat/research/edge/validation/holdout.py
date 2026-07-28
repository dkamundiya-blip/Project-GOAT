"""
Project GOAT v0.6 — Holdout Access Gate & Capability Isolation

Implements strict HoldoutAccessGate state machine (SEALED -> AUTHORIZED -> ACCESSED -> CONSUMED)
preventing unauthorized or pre-registered holdout partition access.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from goat.research.edge.models import compute_confirmatory_audit_id
from goat.research.edge.validation.exceptions import HoldoutAccessError
from goat.research.edge.validation.models import HoldoutState


class HoldoutAccessGate:
    """Security gate preventing exploratory holdout access and enforcing audit identity pre-registration."""

    def __init__(self) -> None:
        self._state = HoldoutState.SEALED
        self._audit_id: str | None = None
        self._validation_run_id: str | None = None
        self._edge_id: str | None = None
        self._hypothesis_version: str | None = None
        self._policy_hash: str | None = None
        self._dataset_fingerprint: str | None = None
        self._holdout_partition_identity: str | None = None
        self._accessed_at_utc: str | None = None
        self._consumed_at_utc: str | None = None
        self._bytes_read: int = 0

    @property
    def current_state(self) -> HoldoutState:
        return self._state

    @property
    def audit_id(self) -> str | None:
        return self._audit_id

    @property
    def is_authorized(self) -> bool:
        return self._state in (HoldoutState.AUTHORIZED, HoldoutState.ACCESSED, HoldoutState.CONSUMED)

    @property
    def bytes_read(self) -> int:
        return self._bytes_read

    def authorize_access(
        self,
        edge_id: str,
        hypothesis_version: str,
        policy_hash: str,
        dataset_fingerprint: str,
        holdout_partition_identity: str,
        validation_run_id: str,
    ) -> str:
        """Pre-register confirmatory audit identity and transition gate from SEALED to AUTHORIZED."""
        if self._state != HoldoutState.SEALED:
            raise HoldoutAccessError(
                f"Cannot authorize HoldoutAccessGate in state '{self._state.value}'; gate must be SEALED"
            )

        # Compute deterministic AUD_<HEX16> confirmatory audit identity
        audit_id = compute_confirmatory_audit_id(
            validation_run_id=validation_run_id,
            frozen_hypothesis_version=hypothesis_version,
            dataset_fingerprint=dataset_fingerprint,
            policy_hash=policy_hash,
            holdout_partition_identity=holdout_partition_identity,
        )

        self._edge_id = edge_id
        self._hypothesis_version = hypothesis_version
        self._policy_hash = policy_hash
        self._dataset_fingerprint = dataset_fingerprint
        self._holdout_partition_identity = holdout_partition_identity
        self._validation_run_id = validation_run_id
        self._audit_id = audit_id
        self._state = HoldoutState.AUTHORIZED

        return audit_id

    def access_holdout(self, accessor_fn: Callable[[], Any]) -> Any:
        """Execute holdout data accessor callback under strict state transition rules."""
        if self._state == HoldoutState.SEALED:
            raise HoldoutAccessError("Holdout access denied: Gate is SEALED (authorization required)")
        elif self._state == HoldoutState.CONSUMED:
            raise HoldoutAccessError("Holdout access denied: Gate is CONSUMED (re-access strictly prohibited)")
        elif self._state == HoldoutState.ACCESSED:
            raise HoldoutAccessError("Holdout access denied: Concurrent access in progress")
        elif self._state != HoldoutState.AUTHORIZED:
            raise HoldoutAccessError(f"Holdout access denied in state '{self._state.value}'")

        # AUTHORIZED -> ACCESSED
        self._state = HoldoutState.ACCESSED
        self._accessed_at_utc = datetime.now(timezone.utc).isoformat()

        try:
            result = accessor_fn()
            # Estimate bytes read for verification tracing
            if isinstance(result, (bytes, bytearray)):
                self._bytes_read = len(result)
            elif hasattr(result, "memory_usage"):
                self._bytes_read = int(result.memory_usage(deep=True).sum())
            else:
                self._bytes_read = 1024
        except Exception as exc:
            # Crash safety: Failure after ACCESSED lock must remain CONSUMED (fail-closed)
            self._state = HoldoutState.CONSUMED
            self._consumed_at_utc = datetime.now(timezone.utc).isoformat()
            raise HoldoutAccessError(f"Holdout accessor raised exception: {exc}") from exc

        # ACCESSED -> CONSUMED
        self._state = HoldoutState.CONSUMED
        self._consumed_at_utc = datetime.now(timezone.utc).isoformat()

        return result
