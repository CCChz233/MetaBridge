"""The day-1 contract: records validate, and the two transfer modes differ."""

from __future__ import annotations

import json
from pathlib import Path

from evolution.record import validate_record
from evolution.transfer import TransferMode, transfer
from improvers.protocol import ImproverCheckpoint


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "experiments" / "schema" / "example_record.json"


def test_example_record_matches_schema() -> None:
    record = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    validate_record(record)


def test_policy_transfer_drops_archive_and_full_state_keeps_it() -> None:
    checkpoint = ImproverCheckpoint(
        improver_id="I_SWE",
        parent_id="I0",
        analyzer_hash="analyzer",
        proposer_hash="proposer",
        mutator_hash="mutator",
        selector_hash="selector",
        archive_ids=("swe-case-1",),
    )

    policy = transfer(checkpoint, TransferMode.POLICY)
    full_state = transfer(checkpoint, TransferMode.FULL_STATE)

    assert policy.checkpoint.analyzer_hash == "analyzer"
    assert policy.checkpoint.mutator_hash == "mutator"
    assert policy.checkpoint.archive_ids == ()
    assert "archive" in policy.reset

    assert full_state.checkpoint.archive_ids == ("swe-case-1",)
    assert full_state.reset == ()
    assert policy.checkpoint.archive_ids != full_state.checkpoint.archive_ids
