"""Validate one Improver iteration against the experiment-record schema.

The schema file is the contract. This module only checks that a record matches
it, so later runs can be compared without reconstructing the story from
unlabeled files.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "schema"
    / "iteration_record.schema.json"
)


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record: dict, schema: dict | None = None) -> None:
    validator = Draft202012Validator(schema or load_schema())
    errors = sorted(validator.iter_errors(record), key=lambda err: list(err.path))
    if errors:
        message = "\n".join(error.message for error in errors)
        raise ValueError(message)
