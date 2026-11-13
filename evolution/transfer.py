"""What moves when an Improver changes benchmarks.

Policy transfer keeps the evolved Analyzer and Mutator and drops source
experience. Full-state transfer keeps that experience as well. Neither mode
moves the source harness: target optimization starts from a fresh harness.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from improvers.protocol import ImproverCheckpoint


class TransferMode(str, Enum):
    NONE = "none"
    POLICY = "policy"
    FULL_STATE = "full_state"


POLICY_RETAINED = (
    "analyzer",
    "mutator",
    "proposer",
    "selector",
)

POLICY_RESET = (
    "archive",
    "case_history",
    "task_memory",
    "source_trajectories",
)


@dataclass(frozen=True)
class TransferredImprover:
    checkpoint: ImproverCheckpoint
    mode: TransferMode
    retained: tuple[str, ...]
    reset: tuple[str, ...]


def transfer(checkpoint: ImproverCheckpoint, mode: TransferMode) -> TransferredImprover:
    """Freeze an Improver for a target-benchmark run.

    Policy transfer clears the archive. Compiled source-specific heuristics
    can remain inside the Analyzer and Mutator artifacts; this function does
    not inspect or remove them.
    """

    if mode is TransferMode.NONE:
        return TransferredImprover(
            checkpoint=replace(checkpoint, archive_ids=()),
            mode=mode,
            retained=POLICY_RETAINED,
            reset=POLICY_RESET,
        )
    if mode is TransferMode.POLICY:
        return TransferredImprover(
            checkpoint=replace(checkpoint, archive_ids=()),
            mode=mode,
            retained=POLICY_RETAINED,
            reset=POLICY_RESET,
        )
    if mode is TransferMode.FULL_STATE:
        return TransferredImprover(
            checkpoint=checkpoint,
            mode=mode,
            retained=POLICY_RETAINED + ("archive", "case_history", "task_memory"),
            reset=(),
        )
    raise ValueError(f"Unknown transfer mode: {mode}")
