# Spec 0001: Experiment framework

Status: draft
Date: 2026-10-24
Constitution refs: §2, §3, §5, §6, §7, §9.5
Related decisions: 0001 (member removal), 0002 (pretrained models)

Items marked **[PROVISIONAL]** are defaults chosen without a final
decision. They MAY be changed, but only by amending this spec.

## 1. Purpose and scope

Experiments guide future specs and decisions. This spec defines:

1. how an experiment is recorded (Section 2);
2. the shared evaluation protocol that makes experiments comparable
   (Section 3);
3. the reproducibility rules (Section 4);
4. the experiment lifecycle (Section 5).

In scope:

- Experiments on preprocessing and matching/decision (modules 3, 4),
  and on the models behind them (module 8).
- Both from-scratch and pretrained models (Decision 0002).

Out of scope for now:

- Using employee photos. Experiments use **public data only** until a
  later decision. Any experiment that adds employee data MUST first
  follow §6 (consent) and Decision 0001.
- Face detection experiments (module 2) and the "no face" case.
  LFW images are already cropped, so they cannot test detection.
  These need their own data and an amendment to this spec.
- Multiple faces per photo (Open Item §9.1).

## 2. Experiment record

Every experiment MUST have one record file:
`docs/experiments/EXP-NNNN-short-name.md` (NNNN is a sequential number).

### 2.1 Required fields

Each experiment MUST contain all of the following. A field that does
not apply MUST say "n/a" with a one-line reason, not be omitted.

| # | Field              | Requirement                                |
|---|--------------------|--------------------------------------------|
| 1 | Hypothesis         | Falsifiable. Names the metric and the      |
|   |                    | expected outcome. Written **before** the   |
|   |                    | run.                                       |
| 2 | Configuration      | Everything needed to rerun: dataset and    |
|   |                    | split manifest versions, split and training|
|   |                    | seeds, preprocessing, code commit, config  |
|   |                    | file, software versions, hardware.         |
| 3 | Model              | Architecture, input size, embedding size,  |
|   |                    | parameter count, loss. Origin: from        |
|   |                    | scratch or pretrained.                     |
| 4 | Training strategy  | From scratch: data, augmentation,          |
|   |                    | optimizer, schedule, stopping rule.        |
|   |                    | Pretrained: see 2.2.                       |
| 5 | Hyperparameters    | All values used, plus how they were        |
|   |                    | chosen and on which set. "n/a" if none.    |
| 6 | Metrics            | The metrics of Section 3.7, with           |
|   |                    | uncertainty.                               |
| 7 | Result             | Plain numbers and tables. No opinions.     |
| 8 | Interpretation     | Whether the hypothesis held, the limits    |
|   |                    | of the evidence, and which spec or         |
|   |                    | decision this feeds.                       |

### 2.2 Pretrained models

If the model is pretrained, the record MUST look up and state:

- name, version, and source URL;
- retrieval date and file checksum;
- licence, and whether it allows the company's intended use;
- training data, and whether it may overlap with the evaluation
  identities (see 3.9);
- use: frozen, or fine-tuned (and on what data);
- employee data exposure: none, or fine-tuned on employee data
  (this decides whether Decision 0001 retraining applies).

Weights MUST NOT be committed. Only a manifest (name, source,
checksum, licence) is committed.

### 2.3 Other record rules

- Record header: id, title, date, author, status, constitution
  refs, related experiments.
- Negative and inconclusive results MUST be recorded.
- After the status is `done`, the record is not edited. Corrections
  go in a dated "Amendment" section at the end.
- Interpretation MUST NOT claim more than the reported uncertainty
  supports.

### 2.4 Record template

```markdown
# EXP-NNNN: <title>

Status: planned | running | done | invalid
Date: YYYY-MM-DD
Author:
Constitution refs:
Related experiments:

## Hypothesis
## Configuration
- Dataset / manifest version:
- Split seeds:
- Training seeds:
- Code commit:
- Config file:
- Software versions:
- Hardware:
## Model
## Training strategy
## Hyperparameters
## Metrics
## Result
## Interpretation
```

## 3. Shared evaluation protocol

Every experiment that reports FAR/FRR MUST use this protocol.
Deviations MUST be declared in the record and the result MUST NOT be
compared directly with protocol-conforming results.

### 3.1 Data

- **Evaluation data:** LFW. Its licence/terms of use MUST be checked
  and recorded before the first experiment (§6).
- Images and weights MUST NOT be committed. Only manifests
  (identity and file ids) are committed.
- LFW is small and most identities have one image. Eligibility
  rules in 3.2 follow from that.
- **Training data for from-scratch models** is **not yet decided**
  (see Open Items). LFW alone is probably too small to train a
  model from scratch. A from-scratch model MUST NOT train on any
  identity used in members, strangers, evaluation, or test sets.

### 3.2 Identity roles

For each **split seed**, the identities are assigned roles:

- **Members:** M identities. **[PROVISIONAL]** M = 20, matching the
  expected company size. Each member MUST have enough images for
  enrollment, evaluation probes, and test probes.
- **Strangers:** other identities, divided into **evaluation
  strangers** and **test strangers**. These two groups MUST be
  disjoint from each other and from the members.

### 3.3 Image roles for members

Each member's images are divided, without overlap, into:

- **enrollment:** k images used to build the template.
  **[PROVISIONAL]** k = 3.
- **evaluation probes:** used to tune the threshold.
  **[PROVISIONAL]** at least 1 per member.
- **test probes:** used only for the final numbers.
  **[PROVISIONAL]** at least 2 per member.

Each stranger identity contributes images only to its own group.

### 3.4 Evaluation set and test set

- The **evaluation set** (evaluation probes + evaluation strangers)
  is used for threshold tuning and model selection.
- The **test set** (test probes + test strangers) is used only for
  the final reported numbers, once per experiment configuration.
  It MUST NOT be used to tune anything.
- Splits MUST be fixed and versioned as manifest files (§7).

### 3.5 Decision rule

Matching is evaluated end to end against the system contract (§2 of
the constitution), on face crops:

1. compute the embedding of the probe;
2. compare it with every enrolled template, giving similarity
   scores;
3. if the best score is at or above the threshold, output that
   member; otherwise output `STRANGER`.

If the choice is uncertain and the threshold cannot settle it, the
output MUST be `STRANGER` (§5). The similarity measure and the way
a template is built from the k images MUST be recorded.

### 3.6 Threshold

- The threshold is tuned on the evaluation set only, to meet both
  targets together (§5): FAR < 5% and FRR < 3%.
- If no threshold meets both on the evaluation set, the record MUST
  say so and report the threshold with the smallest overshoot.
- The threshold used MUST be reported with the results.

### 3.7 Metrics

Reported on the **test set**:

| Metric            | Definition                                  |
|-------------------|---------------------------------------------|
| FAR               | stranger probes output as a member, divided |
|                   | by all stranger probes                      |
| FRR               | member probes output as `STRANGER`, divided |
|                   | by all member probes                        |
| Threshold         | the value tuned in 3.6                      |
| Misidentification | member probes output as the **wrong**      |
| rate (MIR)        | member, divided by all member probes        |
| EER and ROC       | for threshold-free comparison               |
| Latency           | p50 and p95 per module and end to end, per  |
|                   | photo, with the hardware stated             |
| Training time     | wall-clock time and hardware of a full run  |
| Size              | parameter count and file size               |

Notes:

- FAR and FRR follow the constitution's definitions. A member
  identified as the wrong member is neither, so it is reported
  separately as MIR. See Open Items.
- Training time feeds the open question in Decision 0001.
- The constitution's accuracy targets (§5) and latency budget (§3)
  are pass/fail criteria. The target hardware is not yet defined,
  so latency is reported with the hardware used and is not final.

### 3.8 Uncertainty

- With about 20 members, a single split has few probes, so FRR and
  FAR are noisy. Results MUST be reported over R random identity
  splits. **[PROVISIONAL]** R = 10, with a fixed list of seeds.
- Report mean and standard deviation across splits, plus a 95%
  confidence interval (for example bootstrap over identities).
- A target counts as met only if the point estimate meets it. A
  target counts as clearly met only if the upper bound of the
  interval also meets it. The record MUST state which case applies.
- A difference between two experiments is only claimed when the
  intervals do not overlap, or a paired test is reported.

### 3.9 Leakage checks

- Evaluation identities MUST NOT appear in the training data of any
  model under test.
- For pretrained models, overlap with LFW identities MUST be
  checked against the model's documented training data. If overlap
  cannot be excluded, the result MUST be marked "possible leakage"
  and MUST NOT be used to claim the targets are met.

## 4. Reproducibility rules

This section partly answers Open Item §9.5. The test framework and
the config file format are still undecided.

- **Seeds:** all random sources (Python, NumPy, PyTorch, data
  loader, split generation) MUST be seeded from values recorded in
  the record. Split seeds and training seeds are separate.
  **[PROVISIONAL]** from-scratch models use at least 3 training
  seeds.
- **Determinism:** deterministic algorithms SHOULD be enabled. If
  some operation cannot be deterministic (for example some GPU
  ops), the record MUST say so.
- **Configuration:** every hyperparameter and path comes from one
  config file stored with the record. No values hard-coded in
  scripts. The format is to be chosen.
- **Dependencies:** Python, PyTorch, CUDA (if used), OpenCV, and
  all other package versions MUST be pinned and recorded.
- **Code:** the exact git commit MUST be recorded. Results from
  uncommitted code are invalid.
- **Hardware:** CPU, GPU, RAM, and OS MUST be recorded.
- **Data:** dataset version and split manifest versions (with
  checksums) MUST be recorded.
- **Rerun:** a reader MUST be able to repeat the experiment from the
  record alone. A result that cannot be reproduced within the
  reported uncertainty makes the experiment `invalid`.
- **Privacy:** records, logs, and manifests MUST NOT contain
  personal data of employees (§6).

## 5. Lifecycle

1. `planned`: hypothesis, configuration, and metrics are written
   before running.
2. `running`
3. `done`: all required fields filled in, result and interpretation
   recorded.
4. `invalid`: the protocol was broken or the result could not be
   reproduced. The record is kept with the reason.

An experiment feeds a decision only when it is `done` and its
interpretation names the spec or decision it supports.

### Recommended first experiment

**EXP-0001 (dataset audit):** count LFW identities and images per
identity, check how many identities can serve as members under
3.2 and 3.3, confirm the licence, and decide whether the
provisional values of M, k, and the probe counts are feasible. No
model is needed. It also tells whether another public dataset is
required for training.

## 6. Acceptance criteria

This spec is done when:

- the record template exists in the repository;
- a split generator produces versioned manifests following Section
  3 from a seed;
- an evaluation script reports all metrics of 3.7 with the
  uncertainty of 3.8;
- both have unit tests (§7), and a run is reproducible from a
  record.

## 7. Open items

These are not decided. Experiments MUST NOT assume an answer.

1. **Training data for from-scratch models:** LFW alone is likely
   too small. Which additional public dataset (and licence)?
2. **Target hardware:** not defined. It must be fixed before latency
   can be judged against the 3-second budget (§3).
3. **Wrong-member outputs:** should MIR be folded into FAR or FRR,
   or be a third target? The constitution is silent.
4. **Detection and "no face" experiments:** need a data source and a
   spec amendment.
5. **Provisional values:** M, k, probe counts, R, and number of
   training seeds. Validate in EXP-0001.
6. **Test framework and config format:** constitution §9.5.
