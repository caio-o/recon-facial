# 0002: Member removal policy (data, embeddings, retraining)

Status: accepted
Date: 2026-10-13
Constitution refs: §6 (Data, Privacy and Consent), §9.2 (Open Items)
Related specs: member removal, model training and evaluation

## Context

The constitution requires that when a member is removed, all their
photos and related personal data, raw or processed, MUST be deleted
(§6).

Employee photos are part of the data used to train the model
weights, not only to build matching templates. Deleting photos and
embeddings therefore does not remove everything derived from the
person: their face may remain encoded in the trained weights.

This decision defines what removal means for each kind of data, and
whether and when the model must be retrained. It resolves open item
§9.2.

## Options Considered

1. **Strict: retrain immediately on every removal**
   - Pro: the model never outlives the person's data.
   - Con: costly, and impractical when several removals are close
     together.
2. **Moderate: delete data immediately, retrain within a fixed
   deadline**
   - Pro: data is gone at once, the model is cleaned within a known
     time, and removals inside the window can share one training run.
   - Con: for a limited time, the old weights still exist.
3. **Lenient: delete data only, treat weights as anonymous**
   - Pro: cheapest.
   - Con: not supported. Weights trained on a person's photos may
     encode their face, which conflicts with §6.

## Decision

Option 2: moderate, with a **fixed 30-day retraining deadline**.

### On removal (immediately)

The following MUST be deleted for the removed person:

- raw photos
- embeddings and matching templates
- any derived or augmented copies of their photos
- entries in training, test, and evaluation sets
- cached or intermediate data, and logs that contain their images
  or embeddings

The person MUST also be excluded from all future training, testing,
and evaluation. Once their templates are deleted, the system
returns `STRANGER` for them.

### Retraining (within 30 days)

- The model MUST be retrained, without the removed person's data,
  and replace the old model within **30 days** of the removal.
- The deadline counts from the removal date of each person.
- Several removals inside the window MAY share one retraining run.
  The earliest removal date in the batch sets the deadline.
- Retraining MAY happen earlier. Any retraining run that excludes
  the person satisfies the requirement.
- After the retrained model passes evaluation (FAR < 5%, FRR < 3%,
  per constitution §5), it replaces the old one.
- Templates of the remaining members MUST be recomputed with the
  new model, since embeddings from different models are not
  comparable.

### Old models

- After the replacement, the old model, its checkpoints, and any
  backups MUST be deleted.
- Until then, old models fall under the same local-only and
  least-access rules as other personal data (§6).

### Record keeping

- Each removal MUST be logged with the person's id, the removal
  date, the retraining deadline, and the completion date. The log
  MUST NOT contain face data.
- A removal is complete only when both the immediate deletion and the
  retraining have been done.

## Consequences

- Photos of current members MUST stay available locally, so that
  retraining and template recomputation are possible. This is
  covered by their signed consent and the local-only rule.
- Removal is a two-step process, and the removal spec must describe
  both steps and track the deadline.
- The training pipeline (module 8) must be reproducible and
  runnable on demand, since retraining is now a recurring event.
- If a retrained model fails the accuracy targets, the deadline
  still applies. This case needs a fallback: a plan item, and
  possibly a later decision.
- The constitution should be updated: state in §6 that trained
  weights count as processed personal data, reference this
  decision, and remove open item §9.2.

## Open Questions

- **Training time:** how long a full training run takes on the
  target hardware is not yet known. It MUST be measured. If a run
  takes close to or longer than 30 days of available compute, this
  decision must be revisited.
- **Failed retraining:** what to do if a retrained model misses the
  FAR/FRR targets before the deadline.
- **Verification:** whether to test that a retrained model no longer
  recognizes a removed person (for example, by checking that their
  photos are classified as `STRANGER`).
