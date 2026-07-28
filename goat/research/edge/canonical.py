"""
Project GOAT v0.6 — Canonical Serialization & Deterministic SHA-256 Hashing

Provides a single authoritative canonical serializer for v0.6 scientific identity calculations.
Enforces recursive dictionary key sorting, compact JSON formatting, UTF-8 encoding, and
stable Enum serialization without operational metadata leakage.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel


def freeze_structure(val: Any) -> Any:
    """Recursively freeze nested data structures into immutable types.

    - dict / MappingProxyType -> MappingProxyType where all values are recursively frozen.
    - list / tuple / set -> tuple where all elements are recursively frozen.
    - Primitives -> preserved as-is.
    """
    if isinstance(val, (dict, MappingProxyType)):
        frozen_dict = {k: freeze_structure(v) for k, v in val.items()}
        return MappingProxyType(frozen_dict)
    elif isinstance(val, (list, tuple, set)):
        return tuple(freeze_structure(x) for x in val)
    return val


def canonicalize_structure(val: Any) -> Any:
    """Recursively convert data structures into canonical primitives for deterministic JSON serialization.

    Rules:
    - Dictionaries / MappingProxyType: Sorted by key lexicographically; values canonicalized recursively.
    - Lists / Tuples: Canonicalized recursively element-by-element, preserving sequence order.
    - Sets: Sorted by canonical string representation, then converted to list.
    - Enums: Replaced with their raw value (`enum.value`).
    - Pydantic BaseModel: Converted via `.model_dump(mode="json")` then canonicalized.
    - Floats: Must be finite numbers; NaN or Infinity raise ValueError.
    - Primitive types (str, int, bool, None): Preserved as-is.
    """
    if isinstance(val, enum.Enum):
        return canonicalize_structure(val.value)
    elif isinstance(val, BaseModel):
        return canonicalize_structure(val.model_dump(mode="json"))
    elif isinstance(val, (dict, MappingProxyType)):
        return {str(k): canonicalize_structure(v) for k, v in sorted(val.items(), key=lambda item: str(item[0]))}
    elif isinstance(val, (list, tuple)):
        return [canonicalize_structure(x) for x in val]
    elif isinstance(val, set):
        elements = [canonicalize_structure(x) for x in val]
        return sorted(elements, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
    elif isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Cannot canonically serialize non-finite float '{val}'")
        if val == 0.0:
            val = 0.0
        return round(val, 10)
    elif isinstance(val, (int, str, bool)) or val is None:
        return val
    else:
        raise TypeError(f"Type '{type(val).__name__}' is not canonically serializable")


def canonical_json(val: Any) -> str:
    """Serialize value to compact, deterministic canonical JSON string."""
    canon_obj = canonicalize_structure(val)
    return json.dumps(canon_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(val: Any, length: int | None = None) -> str:
    """Compute deterministic SHA-256 hex digest of a canonical payload."""
    json_str = canonical_json(val)
    digest = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    if length is not None:
        return digest[:length]
    return digest
