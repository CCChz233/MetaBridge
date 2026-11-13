# MetaBridge

### Cross-Benchmark Generalization of Self-Improving Agents

**Can an Improver learn to improve beyond the benchmark it evolved on?**

An Improver evolved on SWE-bench may become better at optimizing agents for SWE-bench. That result leaves open whether it learned to improve agents, or only learned how to improve agents on that benchmark. MetaBridge measures the difference.

| | |
| --- | --- |
| **Why this question** | Benchmark gains do not identify what a self-improving system learned. An Improver can exploit the source task distribution, the source harness, and source-specific failure modes. |
| **What is still missing** | Prior work already asks whether an agent or a harness works on a new benchmark, and whether self-improvement transfers across tasks. Those results do not isolate the Improver, and they do not separate its improvement policy from the benchmark-specific experience it accumulated. |
| **What MetaBridge does** | Treat the Improver as the object of study. Evolve it on SWE-bench Verified, freeze it, and test whether it optimizes a freshly initialized agent more effectively on Terminal-Bench than an unevolved Improver. |

> Can an Improver evolved on one benchmark acquire transferable meta-improvement capabilities that enable more effective agent optimization on unseen benchmarks?

Positive transfer, no transfer, and negative transfer are all admissible outcomes. The experiment measures which one occurs, and which part of the Improver produces it.

**Project status:** research prototype. The protocol below is the study definition. It is not yet a completed experiment.

**Core research theme:** cross-benchmark generalization of self-improving agents.

---

## 1. Motivation

Self-improving agents iteratively analyze execution trajectories, identify weaknesses, modify their harnesses, and evaluate the resulting candidates.

Performance gains on a source benchmark do not show that the Improver acquired a general improvement capability. An Improver evolved on SWE-bench may learn strategies that are useful only for repository-level software engineering: which tests to read, which harness fields to edit, which failures to trust. Whether those strategies still help when the same Improver optimizes an agent for a different environment, such as Terminal-Bench, is the question.

Placing that Improver on Terminal-Bench changes the task distribution, the execution environment, and the optimization problem. Three outcomes are possible:

- **Positive transfer.** Error analysis, edit strategy, or selection behavior learned on the source benchmark improves optimization on the target benchmark.
- **No transfer.** Source evolution was specific to the source task distribution. The evolved Improver has no reliable advantage.
- **Negative transfer.** Source-specific preferences interfere with improvement in the new environment.

## 2. Research Questions

- **RQ1: Transferability.** Do Improvers evolved on one benchmark outperform their original counterparts when optimizing agents on a different benchmark?
- **RQ2: Transfer mechanisms.** Which Improver components carry cross-benchmark transfer? The first study varies the Analyzer and the Mutator, and holds the Proposer model and the Selector rules fixed.
- **RQ3: Negative transfer.** Under what conditions does benchmark-specific evolution reduce improvement in a new environment, relative to the original Improver?
- **RQ4: Target adaptation.** After the transfer, does the evolved Improver reach a given target-benchmark improvement with less budget than an unevolved Improver?

## 3. Core Idea

MetaBridge separates three levels of generalization.

| Level | Question | Role in this project |
| --- | --- | --- |
| Agent generalization | Can an agent solve tasks from an unseen benchmark? | Context. Not the primary endpoint. |
| Harness generalization | Does an evolved harness remain effective on an unseen benchmark? | Context. Target runs start from a fresh harness, so a source harness is not carried over. |
| Improver generalization | Can an evolved Improver continue to optimize agents on an unseen benchmark? | Primary object of study. |

The transferred object is the improvement mechanism. The final source-benchmark agent and the final source-benchmark harness stay behind.

## 4. Experimental Protocol

**Source benchmark:** SWE-bench Verified

**Target benchmark:** Terminal-Bench

1. **Source evolution.** Evolve an initial Improver, $I_0$, on the source benchmark under a fixed budget.
2. **Improver transfer.** Freeze the evolved Improver, $I_{\mathrm{SWE}}$.
3. **Target optimization.** Apply it to a freshly initialized target harness. The target run does not inherit the SWE-bench harness.
4. **Evaluation.** Measure improvement on held-out target tasks. Evolution tasks, validation tasks, and test tasks are disjoint.

A run of about 10 tasks and 3–5 generations is an engineering check. Confirmatory runs use a larger task set, a frozen validation/test split, and multiple random seeds. The same task agent, initial harness, model, task split, and token budget are used across arms.

### Improver checkpoint

A checkpoint is the unit that moves between benchmarks. It records:

- Analyzer artifact (prompt or code) and its hash
- Mutator artifact and its hash
- Proposer model identity, held fixed in the first study
- Selector rules, held fixed in the first study
- Whether the archive, case history, and task memory are included

### Two transfer settings

- **Policy transfer.** Move the Analyzer and Mutator. Reset the archive, source case history, and task memory.
- **Full-state transfer.** Move the Analyzer, Mutator, and the accumulated archive and experience.

Policy transfer tests the evolved improvement policy. It does not, by itself, prove that the policy is benchmark-agnostic: source-specific heuristics may already be compiled into the Analyzer or Mutator text. Full-state transfer adds the accumulated experience. The contrast asks whether extra source memory helps, hurts, or does nothing on the target benchmark. Later component and content analysis is required to separate general strategies from source-specific rules inside the policy.

## 5. Experimental Arms

| ID | Setting | Improver | Purpose |
| --- | --- | --- | --- |
| E0 | Original | $I_0$, no source evolution | Baseline improvement ability |
| E1 | Cross-benchmark | $I_{\mathrm{SWE}}$, full-state transfer | Transfer with accumulated experience |
| E2 | Policy-only | $I_{\mathrm{SWE}}$, archive and source memory cleared | Policy transfer |
| E3 | In-domain | Improver evolved on Terminal-Bench from $I_0$ | Same-domain reference |

E3 is a reference arm, not an upper bound. It uses the same initial Improver, budget, and evaluation split, with evolution performed on the target benchmark.

## 6. Evaluation Metrics

- **Final performance.** Task success rate after optimization.
- **Improvement gain.** Change from the initial harness on the same split.
- **Improvement efficiency.** Gain per token or per evaluation.
- **Transfer gap.** Source-benchmark improvement minus target-benchmark improvement for the same Improver lineage.
- **Negative transfer.** Target-benchmark gain of $I_{\mathrm{SWE}}$ minus the gain of $I_0$, when that difference is negative.
- **Adaptation efficiency.** Budget required to reach a pre-registered target-benchmark gain.

Primary comparisons use held-out target tasks. Scores from tasks the Improver saw during proposal or selection are reported separately and are not the confirmatory endpoint.

## 7. Architecture

MetaBridge keeps task execution separate from meta-improvement, so an optimizer can be replaced without changing the experimental contrast.

**Task agent**

- Executes benchmark tasks.
- Produces execution trajectories.
- Returns task-level evaluation results. The Improver does not assign its own success label.

**Meta-Improver**

- **Analyzer.** Reads trajectories and states failure causes and improvement opportunities.
- **Proposer.** Turns an analysis into an improvement strategy. Its base model stays fixed while Analyzer and Mutator are the components under study.
- **Mutator.** Turns a strategy into a concrete harness, prompt, or code change.
- **Selector.** Keeps, rejects, or rolls back a candidate from evaluation results. Its decision rule stays fixed in the first study.

**Evolution controller**

- Runs the iteration loop.
- Stores parent links, archives, and checkpoints.
- Records evaluations and token cost.
- Applies policy transfer or full-state transfer.

GEPA and DGM are references for the optimizer and the archive. They are not required dependencies. The checkpoint and the experiment record stay the same if the optimizer changes.

## 8. Initial Technology Stack

| Component | Initial choice |
| --- | --- |
| Task agent | mini-SWE-agent |
| Alternative execution environment | OpenHands |
| Improver optimization | GEPA or a custom meta-improver |
| Evolution and archive | DGM-inspired |
| Source benchmark | SWE-bench Verified |
| Target benchmark | Terminal-Bench |
| Model providers | DeepSeek and Qwen APIs |

These are starting choices. A local checkout of upstream GEPA may sit in `gepa/` for reading. That checkout is not this project, and it is not committed here.

## 9. Project Structure

```text
MetaBridge/
├── README.md
├── configs/
│   ├── improver/
│   ├── benchmarks/
│   └── experiments/
├── agents/
│   ├── task_agent/
│   └── harness/
├── improvers/
│   ├── protocol.py
│   ├── analyzer/
│   ├── proposer/
│   ├── mutator/
│   └── selector/
├── evolution/
│   ├── transfer.py
│   └── record.py
├── benchmarks/
│   ├── swebench/
│   └── terminalbench/
├── experiments/
│   ├── schema/
│   ├── source_evolution/
│   ├── policy_transfer/
│   └── target_adaptation/
├── evaluation/
├── scripts/
└── results/
```

## 10. Experiment Record

Every Improver iteration appends one record that validates against [`experiments/schema/iteration_record.schema.json`](experiments/schema/iteration_record.schema.json). The fields are:

| Field | Content |
| --- | --- |
| `improver_id` | Checkpoint id of the current Improver |
| `parent_id` | Parent checkpoint, if any |
| `source_benchmark` | Benchmark on which this lineage evolved |
| `target_benchmark` | Benchmark being optimized in this iteration |
| `mutation` | The concrete Analyzer, Mutator, harness, prompt, or code change |
| `task_results` | Per-task outcomes for this iteration |
| `performance` | Success rate on the declared split |
| `token_cost` | Tokens consumed by the task agent and by the Improver |
| `transfer_mode` | `none`, `policy`, or `full_state` |

The record also stores the arm id, generation, seed, split, and component hashes. Those fields are what make a later claim of the form “this generation transferred and that one did not” checkable against the log, rather than against a pile of unlabeled JSON.

## 11. Roadmap

- Freeze a reproducible $I_0$: task agent, model, Selector rule, and initial harness.
- Run source-domain evolution and save every Improver checkpoint.
- Implement policy transfer and full-state transfer from those checkpoints.
- Run the SWE-bench to Terminal-Bench arms E0–E3 under a matched budget.
- Compare improvement curves, including negative transfer.
- Measure target-domain adaptation efficiency.
- Extend the same protocol to additional benchmarks only after the first contrast is reproducible.

## 12. Research Scope

MetaBridge studies the generalization of self-improvement mechanisms: their transfer, their failure to transfer, and their adaptation on a new task environment.

The first study uses coding and terminal agents. The deliverable is a measurement framework for cross-benchmark self-improvement, centered on the Improver rather than on a leaderboard score for one benchmark.
