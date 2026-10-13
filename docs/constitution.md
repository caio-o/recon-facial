# Constitution

Governing principles for the face recognition project. All specs,
plans, tasks, and code MUST comply with this document. Where this
file says MUST or MUST NOT, it is binding. SHOULD and MAY are
recommendations and options.

## 1. Purpose and Scope

- **Project:** a facial recognition system for a small company.
- **Goal:** recognize a company member in a photo and distinguish
  them from strangers.
- **Status:** new (greenfield) project.
- **Users:** the company's staff (about 20 enrolled members).
- **Design target:** one face per photo.

## 2. System Contract

Input: a single photo taken by the entrance camera.

| Situation              | Output                     |
|------------------------|----------------------------|
| Known member           | identity: name + id        |
| Stranger or uncertain  | `STRANGER`                 |
| No face detected       | empty output               |

- Individual modules MAY have their own I/O, but each MUST document
  its contract in its spec.
- The end-to-end system MUST honor the table above.
- Behavior for photos with multiple faces is **unspecified** (see
  Open Items). No spec may assume a behavior until it is defined.

## 3. Technical Stack

- **Language:** Python.
- **ML framework:** PyTorch.
- **Support libraries:** OpenCV where useful.
- **Models:** MUST be trained from scratch. Pretrained weights MUST
  NOT be used.
- **Deployment:** local only, on a single device or a local server.
  No cloud inference and no external services at runtime.
- **Latency:** the full pipeline MUST return a result in under
  3 seconds per photo, on the target hardware.

## 4. Architecture

The system is modular. Each module has a single responsibility, a
documented input/output contract, and its own unit tests.

Runtime modules:

1. **Image source:** supplies the photo (entrance camera).
2. **Face detection:** finds the face in the photo.
3. **Preprocessing:** prepares the face for the model.
4. **Matching / decision:** compares the face to enrolled members
   and decides identity or `STRANGER`.
5. **Interface:** presents the output to the user or caller.
6. **Member enrollment:** adds a new member.
7. **Member removal:** removes a member and their data.

Development module:

8. **Model training, testing and evaluation.**

Rules:

- Modules MUST communicate only through their documented contracts.
- A module MUST NOT access data it does not need.
- Module 8 is for development only and is not part of the runtime
  path.

## 5. Decision Rules and Accuracy

- False accepts (stranger identified as a member) and false rejects
  (member labeled `STRANGER`) are **equally serious**.
- **Targets**, measured on a held-out test set:
  - false accept rate (FAR) under **5%**
  - false reject rate (FRR) under **3%**
- Thresholds MUST be tuned to meet both targets together.
- When a match is uncertain and the thresholds cannot settle it, the
  system MUST output `STRANGER`.
- Evaluation MUST report FAR, FRR, and the threshold used.
- A change that causes either target to be missed MUST NOT be
  merged.

## 6. Data, Privacy and Consent

Face data is biometric and sensitive. These rules take priority over
convenience.

- **Sources:** employee photos and a public dataset. The license of
  any public dataset MUST be checked and recorded.
- **Consent:** an employee's photos MUST NOT enter the database
  until the employee has signed an acknowledgement and consent term.
- **Local storage only:** images, embeddings, and trained models are
  stored locally. They MUST NOT leave the local environment.
- **Least access:** each item is available only to the subsystems
  that need it.
- **Security:** encryption of personal data and password or key
  based authentication SHOULD be implemented.
- **Enrollment:** a member is added only after consent is signed.
  Their photos are then captured and added to the private database.
- **Removal:** when a member is removed, all their photos and
  related personal data, raw or processed, MUST be deleted. This 
  includes the trained weights and embeddings, according to the 
  [Decision 0002: Member Removal Policy](decisions/0002-member-removal-policy.md##decision). 
  As such, model retraining 
  MUST happen according to the §9.2 of this constitution.
- **No personal data in the repository:** photos, embeddings, and
  trained models of employees MUST NOT be committed to version
  control.

## 7. Testing Standards

- Every module MUST have unit tests.
- Trained models MUST be validated with separate **test** and
  **evaluation** sets that are never used for training.
- Evaluation sets MUST be fixed and versioned so results are
  comparable over time.
- The end-to-end latency budget (Section 3) SHOULD be checked on the
  target hardware.
- A module is not done until its tests pass.

## 8. Code Standards

- Code MUST be concise.
- Lines MUST be short (79 characters maximum).
- Variable names SHOULD be short.
- Names MUST use `snake_case` (underscores). Camel case MUST NOT be
  used.
- Short names MUST stay unambiguous within their scope. Public
  function and module names SHOULD be clear enough to read without
  context.

## 9. Open Items

These are undecided. Specs MUST NOT assume an answer. Each needs a
decision before the related spec is finalized.

1. **Multiple faces in one photo:** behavior is to be defined later
   (for example reject, use the largest face, or return one result
   per face).
2. **Retraining on member removal:** whether removal must trigger
   retraining, since embeddings and trained weights may encode a
   removed person's face; according to the decision 
   [Decision 0002: Member Removal Policy](decisions/0002-member-removal-policy.md##decision)
    a retraining of the face 
   recognition models (which were trained on the member's data) 
   MUST happen within a time window of 30 days after the member's 
   removal.
3. **Entrance photo retention:** how long photos from the camera
   are kept. **Provisional default:** photos are processed and not
   stored, until this is decided.
4. **Test framework and reproducibility:** test framework (for
   example pytest), random seeds, dependency pinning, and config
   files for hyperparameters are not yet chosen.

## 10. Governance

- This constitution overrides specs, plans, and tasks that conflict
  with it.
- Amendments MUST be written, dated, and give a reason.
- Open Items, once decided, MUST be moved into the relevant section
  and removed from Section 9.
