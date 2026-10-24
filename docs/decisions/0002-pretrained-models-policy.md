# 0002: Pretrained models policy

Status: proposed
Date: 2026-10-24
Constitution refs: §3 (Technical Stack), §6 (Data, Privacy and
Consent), §9 (Open Items), §10 (Governance)
Related decisions: 0001 (member removal policy)
Related specs: 0001 (experiment framework)

## Context

The constitution (§3) says models MUST be trained from scratch and
pretrained weights MUST NOT be used.

The company has about 20 members. A from-scratch face model needs a
large amount of training data, and the only public data currently
planned is LFW, which is small. It is not known in advance whether
a from-scratch model can meet the accuracy targets (§5: FAR < 5%,
FRR < 3%). Only experiments can show whether a pretrained model is
the better choice, so the constitution should not rule it out
beforehand.

Pretrained weights bring risks that from-scratch models do not:

- their licence may restrict use (for example research-only, which
  may not cover a company);
- the data they were trained on may overlap with our evaluation
  data and inflate results;
- they are third-party artifacts that MUST NOT end up in version
  control or leave the local environment;
- they interact with the removal policy of Decision 0001.

## Options Considered

1. **Keep the ban**
   - Pro: simple, no licence or provenance questions.
   - Con: may force a worse system. Experiments could not compare
     approaches.
2. **Allow pretrained models in experiments only**
   - Pro: permits baselines for comparison.
   - Con: a pretrained model that wins could never be used, which
     makes the comparison pointless.
3. **Allow pretrained models in experiments and in the final system,
   under conditions**
   - Pro: the choice is made on evidence. Risks are controlled by
     explicit rules.
   - Con: adds licence, provenance, and storage obligations.

## Decision

Option 3.

### Permission

- Pretrained models MAY be used in experiments.
- A pretrained model MAY be part of the final system if it is
  adopted under the evidence rules below.
- A from-scratch model remains the default when evidence does not
  favor a pretrained one.

### Evidence for adoption

A pretrained model MAY be adopted only if a recorded experiment
(spec 0001) shows all of:

- it meets the accuracy targets of §5 on the test set under the
  shared evaluation protocol;
- it is better than the best from-scratch model under the same
  protocol (intervals not overlapping), **or** no from-scratch model
  meets the targets;
- it meets the latency budget of §3 on the target hardware;
- no leakage is flagged (spec 0001, 3.9).

### Licence and provenance

Before use in an experiment, and again before adoption, the
following MUST be recorded: name, version, source URL, retrieval
date, checksum, licence, and training data.

- If the licence does not clearly allow the company's intended use
  in the final system, the model MAY be used in experiments but MUST
  NOT be adopted.
- If the training data origin or consent status is unknown, the
  record MUST say so. This counts as a risk to be weighed in the
  adoption decision.

### Storage

- Pretrained weights MUST NOT be committed to version control. Only
  a manifest (name, source, checksum, licence) MAY be committed.
- Weights are stored locally and MUST NOT leave the local
  environment (§6).
- The system MUST NOT download weights at runtime (§3: no external
  services at runtime). Weights are placed locally at setup time
  and their checksum is verified.

### Interaction with Decision 0001

Each experiment record and each adopted model MUST state its
employee data exposure:

| Case                                         | Weights count as   | On removal of a member            |
|----------------------------------------------|--------------------|-----------------------------------|
| Pretrained and **frozen**, never trained on  | not personal data  | Delete photos, embeddings,        |
| employee data                                |                    | templates, and the rest of the    |
|                                              |                    | immediate list in 0001. No        |
|                                              |                    | retraining needed. Templates of   |
|                                              |                    | the other members stay valid.     |
| Pretrained and **fine-tuned** on employee    | processed personal | Everything in 0001, including     |
| data                                         | data               | retraining within 30 days.        |
| Trained **from scratch** on employee data    | processed personal | Everything in 0001, including     |
|                                              | data               | retraining within 30 days.        |

Embeddings and templates are personal data in every case.

## Proposed constitution amendments

Amendment date: 2026-10-24.
Reason: whether pretrained models are better than from-scratch ones
for a 20-member system can only be decided by experiments, so the
ban in §3 conflicts with the purpose of the experimentation phase.

- **§3, Models:** replace "Models MUST be trained from scratch.
  Pretrained weights MUST NOT be used." with: "Models MAY be trained
  from scratch or be pretrained, as decided by experiments (see
  [Decision 0002](decisions/0002-pretrained-models-policy.md)).
  Pretrained weights MUST have a recorded licence and provenance,
  MUST NOT be committed to version control, and MUST NOT be
  downloaded at runtime."
- **§6, Sources:** add "pretrained model weights" to the sources
  and require their licence to be checked and recorded.
- **§6, No personal data in the repository:** add "pretrained
  weights" to the items that MUST NOT be committed.
- **§6, Removal:** state that trained weights count as processed
  personal data only when they were trained or fine-tuned on the
  member's data (Decision 0002).
- **§9:** add open items for target hardware and for the training
  data of from-scratch models. Fix the numbering, which currently
  skips item 3.

## Consequences

- Experiments can compare from-scratch and pretrained models under
  one protocol, and a pretrained winner can reach production.
- The spec 0001 record template includes the pretrained-model
  fields and the employee data exposure field.
- The system needs a documented local setup step to obtain and
  verify weights, since runtime download is not allowed.
- If a pretrained model is adopted and frozen, member removal is
  cheaper, because retraining is not needed. Decision 0001 still
  applies in full to anything trained on employee data.
- Adoption can be blocked by licence terms even when a model
  performs best.

## Open Questions

- **Candidate models:** which pretrained face models to evaluate,
  and what their licences and training data are. This MUST be
  looked up for each candidate.
- **Frozen weights and privacy:** a frozen model trained only on
  third-party data is treated here as not containing employee data.
  Confirm this reading with whoever is responsible for privacy
  compliance.
- **Third-party consent:** whether the consent status of a
  pretrained model's own training data is acceptable for the
  company. This may need a separate decision.
- **Adoption margin:** whether "better than the best from-scratch
  model" needs a minimum margin beyond non-overlapping intervals.
