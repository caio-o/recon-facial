# Spec 0001: Experiment framework

Status: draft
Date: 2026-10-24
Last amended: 2026-10-24 (see Section 8)
Constitution refs: §2, §3, §4, §5, §6, §7, §9.4
Related decisions: 0001 (member removal), 0002 (pretrained models)

Items marked **[PROVISIONAL]** are defaults chosen without a final
decision. They MAY be changed, but only by amending this spec.

## 1. Purpose and scope

Experiments guide future specs and decisions. This spec defines:

1. how an experiment is recorded (Section 2);
2. the shared evaluation protocols that make experiments comparable
   (Section 3 for recognition, Section 3A for detection);
3. the reproducibility rules (Section 4);
4. the experiment lifecycle (Section 5).

In scope:

- Experiments on face detection, preprocessing, and
  matching/decision (modules 2, 3, 4), and on the models behind
  them (module 8).
- Both from-scratch and pretrained models (Decision 0002).

Out of scope for now:

- Using employee photos. Experiments use **public data only** until a
  later decision. Any experiment that adds employee data MUST first
  follow §6 (consent) and Decision 0001.
- Pipeline-level evaluation (detector and matcher together on
  uncropped photos). It needs its own protocol once a detector is
  chosen (Section 7).
- Multiple faces per photo (Open Item §9.1).

## 2. Experiment record

Every experiment MUST have one record file:
`experiments/EXP-NNNN-short-name.md` (NNNN is a sequential number).

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
| 6 | Metrics            | The metrics of Section 3.7 or 3A.5, with   |
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
  identities or images (see 3.9 and 3A.7);
- use: frozen, or fine-tuned (and on what data);
- employee data exposure: none, or fine-tuned on employee data
  (this decides whether Decision 0001 retraining applies).

Weights MUST NOT be committed. Only a manifest (name, source,
checksum, licence) is committed.

### 2.3 Other record rules

- Record header: id, title, date, author, status, constitution
  refs, related experiments.
- Negative and inconclusive results MUST be recorded.
- Detection records MUST also state the detector's output format
  (box convention, confidence score, landmarks if any), because
  preprocessing depends on it.
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

## 3. Shared evaluation protocol: recognition

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

Matching is evaluated against the system contract (§2 of the
constitution), on face crops (the matching module alone, not the
full pipeline):

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

## 3A. Detection evaluation protocol

Applies to experiments on the face detection module (module 2).
The recognition metrics of Section 3 do not apply to it. Rules of
Section 4 apply to both.

### 3A.1 Module contract used in experiments

- **Input:** one decoded, uncropped photo.
- **Output:** zero or more detections, sorted by confidence
  (highest first). Each has a box (pixel coordinates, origin at the
  top-left, x, y, width, height) and a confidence score, and
  optionally landmarks. The output is empty when nothing reaches
  the confidence threshold.
- **Several faces:** behavior is unspecified (Open Item §9.1). The
  detector reports every box it finds. Choosing among boxes is not
  defined here. Metrics that use the highest-scoring box (3A.4) are
  an evaluation convenience for single-face photos and MUST NOT be
  read as the behavior of the system.

### 3A.2 Data

- **Photos with a face (positives):** CelebA, **original uncropped
  ("in-the-wild") images** with face box annotations, not the
  aligned crops, because detection runs before preprocessing.
  EXP-0001 MUST confirm that the boxes exist for the uncropped
  images and MUST check and record the dataset's terms of use
  (§6), which may limit it to research.
- **Label noise:** CelebA photos may contain other faces that are
  not annotated, and its box convention may differ from the one a
  detector uses. EXP-0001 MUST estimate this on a random sample
  reviewed by hand. **[PROVISIONAL]** 200 images.
- **Photos without a face (negatives):** the source is **not yet
  decided**. EXP-0001 chooses it. Requirements:
  - no face in any image (checked by labels, plus manual review of
    every image on which a candidate detector fires with high
    confidence);
  - licence checked and recorded;
  - scenes plausible for an entrance (indoor, outdoor, doors,
    corridors, objects);
  - SHOULD include hard negatives (face-like patterns, people whose
    face is not visible) where they can be labeled reliably.
- Images keep their original size. Any resizing is part of the
  detector's pipeline and MUST be recorded.
- Images MUST NOT be committed. Only manifests are committed.
- CelebA identities may overlap with LFW identities. If CelebA
  images are later used to train a recognition model, 3.9 applies.

### 3A.3 Splits

- An **evaluation set** (confidence threshold, model selection) and
  a **test set** (final numbers only, once per configuration), as
  in 3.4. Both are fixed and versioned manifests.
- Positives are split by identity, so no identity is in both sets.
  Negatives are split by image, by source collection where one is
  given, to keep near-duplicates apart.
- **[PROVISIONAL]** at least 1000 positive and 1000 negative
  images in the test set, so that rates near 1% have a usable
  interval. EXP-0001 confirms.
- A detector trained from scratch MUST NOT train on evaluation or
  test images or identities. Its training data is a separate set.

### 3A.4 Decision rule and error types

- A detection is kept if its confidence is at or above the
  confidence threshold.
- **Correct detection** (on a positive): the highest-scoring kept
  detection has IoU with the annotated box of at least tau.
  **[PROVISIONAL]** tau = 0.5, because annotation conventions
  differ. Recall at tau = 0.7 is reported as information.
- **Missed face** (on a positive), in two kinds, both reported:
  - *no detection*: nothing is kept (the system would give empty
    output for a photo that has a face);
  - *wrong box*: the top detection fails the IoU test (the crop
    passed on is wrong).
- **False detection** (on a negative): at least one kept detection
  (the system would give an output for a photo with no face).
- The confidence threshold is tuned on the evaluation set to meet
  the targets of 3A.6 together. If none does, the record says so
  and reports the threshold with the smallest overshoot. The
  threshold used MUST be reported.

### 3A.5 Metrics

Reported on the **test set**:

| Metric             | Definition                                 |
|--------------------|--------------------------------------------|
| Detection rate     | positives with a correct detection, over   |
|                    | all positives (at tau)                     |
| Missed breakdown   | no-detection rate and wrong-box rate       |
| False detection    | negatives with at least one kept           |
| rate               | detection, over all negatives              |
| Extra detections   | positives with more than one kept          |
|                    | detection. Information only, not an error. |
| Box quality        | mean and median IoU of correct detections  |
| Landmark error     | only if the detector outputs landmarks:    |
|                    | error normalized by inter-ocular distance. |
|                    | Information only.                          |
| Latency            | p50 and p95 per photo, with the hardware   |
|                    | stated (see below)                         |
| Size               | parameter count and file size              |
| Stratified recall  | detection rate by face size, brightness,   |
|                    | and available dataset attributes (for      |
|                    | example blur, eyeglasses). Information     |
|                    | only. Strata under 30 images are flagged.  |

Latency is measured with batch size 1, after warm-up, from the
decoded image in memory to the output list. Decoding time is
reported separately. CPU and GPU are reported separately if both
are used. **[PROVISIONAL]** 10 warm-up runs and at least 200 timed
photos. Face size is the box area as a fraction of the image
area. Brightness is the mean luminance of the image. Bins are
fixed in the manifest.

### 3A.6 Provisional targets and uncertainty

These are budgets for the detector, not constitutional targets.
They exist to keep the end-to-end targets of §5 reachable, and MUST
be revisited after the first results and once pipeline-level
evaluation exists.

- detection rate of at least **99%**;
- false detection rate of at most **1%**;
- p95 latency of at most **500 ms** per photo. This is a share of
  the 3-second budget (§3). The target hardware is not defined, so
  the figure is provisional until it is.

Uncertainty:

- Report a 95% confidence interval: bootstrap over identities for
  positives and over images for negatives.
- Rules of 3.8 apply: a target is met if the point estimate meets
  it, and clearly met only if the relevant interval bound also
  meets it. A difference between experiments is only claimed when
  intervals do not overlap, or a paired test is reported.
- A detector trained from scratch MUST be run with at least 3
  training seeds. A pretrained detector has no training seed, so
  the single fixed split is used.

### 3A.7 Leakage checks

- For pretrained detectors, overlap between the documented
  training data and CelebA, or the chosen negative source, MUST be
  checked.
- If overlap cannot be excluded, the result MUST be marked
  "possible leakage" and MUST NOT be used to claim the targets are
  met (same rule as 3.9).

## 4. Reproducibility rules

This section partly answers Open Item §9.4. The test framework and
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
- **Detection settings:** input resizing, confidence threshold,
  NMS settings, and any other pre- or post-processing of the
  detector are hyperparameters and MUST be in the config file.
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

### Recommended first experiments

**EXP-0001 (dataset audit):** covers the recognition data and the
detection data. For LFW: count identities and images per identity,
check how many identities can serve as members under 3.2 and 3.3,
confirm the licence, and decide whether the provisional values of
M, k, and the probe counts are feasible. For detection (3A.2):
confirm that CelebA original images come with face boxes, check its
terms of use, estimate label noise on a sample, choose and audit
the source of no-face photos, and check that set sizes allow the
provisional targets to be resolved. No model is needed. It also
tells whether another public dataset is required for training.

**EXP-0002 (detector comparison):** the first detector experiment
under 3A, run after EXP-0001 has fixed the data. Its record is
drafted separately.

## 6. Acceptance criteria

This spec is done when:

- the record template exists in the repository;
- a split generator produces versioned manifests following Section
  3 from a seed;
- an evaluation script reports all metrics of 3.7 with the
  uncertainty of 3.8;
- a detection split generator and evaluation script follow Section
  3A and report all metrics of 3A.5 with the uncertainty of 3A.6;
- all of these have unit tests (§7), and a run is reproducible from
  a record.

## 7. Open items

These are not decided. Experiments MUST NOT assume an answer.

1. **Training data for from-scratch models:** LFW alone is likely
   too small. Which additional public dataset (and licence)?
2. **Target hardware:** not defined. It must be fixed before latency
   can be judged against the 3-second budget (§3).
3. **Wrong-member outputs:** should MIR be folded into FAR or FRR,
   or be a third target? The constitution is silent.
4. **Representativeness of detection data:** the entrance camera's
   resolution, distance, angle, and lighting are unknown, and
   CelebA photos are likely easier than entrance conditions, so
   detection results are probably optimistic. Camera specs and
   sample images are needed. Employee photos are allowed only
   under §6.
5. **Provisional values:** M, k, probe counts, R, number of
   training seeds, and the detection values of 3A (targets, tau,
   set sizes, label-noise sample). Validate in EXP-0001.
6. **Test framework and config format:** constitution §9.4.
7. **Source of no-face photos:** chosen by EXP-0001 under 3A.2.
8. **Pipeline-level evaluation:** detector and matcher together on
   uncropped photos, against the full system contract (§2 of the
   constitution, including empty output), needs its own protocol
   once a detector is chosen.

## 8. Amendments

### Amendment 1 (2026-10-24): face detection

Reason: detection (module 2) runs before preprocessing and matching,
and it decides the "no face, empty output" case of the system
contract (§2). Its errors reach every later module, so it needs its
own evaluation protocol before those modules are specified.

Changes:

- Section 1: detection moved into scope. Pipeline-level evaluation
  listed as out of scope.
- Section 2: metrics row and pretrained-model overlap bullet now
  point to Section 3A. Detection records state their output format.
- Section 3: retitled as the recognition protocol. The wording of
  3.5 now says matching is evaluated on face crops, not end to end.
- Section 3A: new detection protocol (contract, data, splits,
  error types, metrics, provisional targets, leakage).
- Section 4: detection settings are hyperparameters.
- Sections 5 and 6: EXP-0001 covers detection data. EXP-0002 added.
  Acceptance criteria extended.
- Section 7: open item 4 replaced, items 7 and 8 added.
- Cross-references to the constitution's test framework item
  changed from §9.5 to §9.4, after its renumbering.

Decisions taken in this amendment: positives come from the
uncropped CelebA images, the source of negatives is left to the
dataset audit, and the detection targets are provisional (99%,
1%, 500 ms).
