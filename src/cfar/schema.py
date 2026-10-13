"""JSON Schema validation before semantic/geometric validation."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .errors import ValidationError

Instance = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]


def spec_path(name: str) -> Path:
    local = ROOT / "spec" / name
    return local if local.exists() else Path(sys.prefix) / "share/cfar/spec" / name


def validate_schema(instance: Instance) -> None:
    def finite(value: Any) -> None:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValidationError("NONFINITE_NUMBER", repr(value))
        if isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)

    finite(instance)
    schema = json.loads(spec_path("instance.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        raise ValidationError("SCHEMA", f"{'/'.join(map(str, error.path))}: {error.message}")


def load_instance(path: str | Path) -> Instance:
    from .validation import validate_instance

    def unique_keys(pairs: list[tuple[str, Any]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValidationError("JSON_DUPLICATE_KEY", key)
            result[key] = value
        return result

    try:
        instance = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValidationError("JSON", str(error)) from error
    validate_instance(instance)
    return instance
