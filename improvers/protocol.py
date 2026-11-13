"""Contracts for the four Improver components.

The first study evolves Analyzer and Mutator. Proposer’s model and Selector’s
decision rule stay fixed, so a cross-benchmark difference can be attributed to
the components that were allowed to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Trajectory:
    task_id: str
    benchmark_id: str
    success: bool | None
    text: str


@dataclass(frozen=True)
class Analysis:
    """Failure causes and improvement opportunities. Not an edit."""

    summary: str
    evidence_task_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Proposal:
    """An improvement strategy. Not yet a harness or code change."""

    summary: str


@dataclass(frozen=True)
class Candidate:
    """A concrete harness, prompt, or code change produced by the Mutator."""

    component: str
    summary: str
    artifact_hash: str


@dataclass(frozen=True)
class Evaluation:
    task_id: str
    success: bool | None


@dataclass(frozen=True)
class Decision:
    action: str
    selected_artifact_hash: str | None
    reason: str


class Analyzer(Protocol):
    def analyze(self, trajectories: Sequence[Trajectory]) -> Analysis:
        """Identify failure causes and improvement opportunities."""


class Proposer(Protocol):
    def propose(self, analysis: Analysis) -> Proposal:
        """Turn an analysis into a strategy. The base model stays fixed."""


class Mutator(Protocol):
    def mutate(self, proposal: Proposal, parent_hash: str) -> Candidate:
        """Turn a strategy into a harness, prompt, or code change."""


class Selector(Protocol):
    def select(
        self,
        parent_hash: str,
        candidates: Sequence[Candidate],
        evaluations: Sequence[Sequence[Evaluation]],
    ) -> Decision:
        """Keep, reject, or roll back. The decision rule stays fixed."""


@dataclass(frozen=True)
class ImproverCheckpoint:
    """The object that transfer moves between benchmarks."""

    improver_id: str
    parent_id: str | None
    analyzer_hash: str
    proposer_hash: str
    mutator_hash: str
    selector_hash: str
    proposer_frozen: bool = True
    selector_frozen: bool = True
    archive_ids: tuple[str, ...] = field(default_factory=tuple)
