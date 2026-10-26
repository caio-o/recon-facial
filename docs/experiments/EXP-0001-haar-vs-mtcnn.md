# EXP-0001: Haar cascade vs MTCNN face detection

Status: running
Date: 2026-10-25
Author: (to fill)
Constitution refs: §3, §4 (module 2), §6, §7
Spec refs: 0001 (Section 3A, Amendment 2)
Decision refs: 0002 (pretrained models)
Related experiments: none

Everything below marked **[PROVISIONAL]** is a pre-registered value.
It MUST be confirmed or changed before Phase 0 starts, and then
frozen (committed) before any metric is computed (Phase 0, G6).

## Hypothesis

Written before the run. Because LFW's faces were found with a
Haar-cascade detector (spec 3A.8), the data favors Haar on
detection rate. Each hypothesis says how to read the result.

**H1, detection rate.** At their selected operating points, MTCNN's
detection rate on the test positives is not lower than the Haar
cascade's.
- Supported if the paired difference (MTCNN minus Haar) is at or
  above 0, or its 95% interval includes 0 with the point estimate
  at or above 0.
- Falsified if MTCNN's point estimate is below Haar's, with the
  interval excluding 0.
- Reading: because the data favors Haar, H1 holding is informative.
  H1 failing is inconclusive.

**H2, false detections.** At selected operating points, MTCNN's
false detection rate on the test negatives is lower than Haar's,
with non-overlapping 95% intervals.
- Falsified if Haar's is lower or equal, or the intervals overlap.
- Reading: the negatives are easy object photos (spec 3A.8), so a
  small difference may not carry over to entrance scenes.

**H3, latency.** The Haar cascade has a lower p95 latency than
MTCNN on the same hardware, and both are at or under 500 ms on LFW
positives (250 x 250 pixels).
- Falsified if MTCNN's p95 is lower than or equal to Haar's, or
  either exceeds 500 ms on positives.
- Latency on the negatives is reported separately (sizes vary).

Expected, stated in advance: both detectors score near 100% on
LFW positives, so detection rate will probably not separate them.
That outcome is recorded as "no separation", not as support for
either detector.

## Configuration

### Data (Phase 0 fills the blanks)

| Item | Value |
|------|-------|
| Positives | LFW, original images (not funneled or aligned) |
| LFW version, source URL, date | (to fill) |
| LFW licence check | (owner's manual check: terms, URL, date) |
| Negatives | Singh's Object Classification dataset |
| Negatives version, source URL, date | (to fill) |
| Negatives licence check | (owner's manual check: terms, URL, date) |
| Image counts | positives, negatives (before and after cap and review) |
| Image sizes | distribution for both sets (to fill) |

### Split (spec 3A.3)

- Single fixed split. Split seed: **[PROVISIONAL]** 0.
- Positives: split by identity, half and half **[PROVISIONAL]**,
  at most 5 images per identity **[PROVISIONAL]**.
- Negatives: split by image, half and half **[PROVISIONAL]**.
- Manifests (ids and checksums only, no images) are versioned.
- Training seeds: n/a (no training).

### Correctness proxy (spec 3A.4)

- Top kept detection contains the image centre, and its width is
  between lo and hi times the image width.
- lo = 0.25, hi = 0.85 **[PROVISIONAL]**.
- Sensitivity ranges: 0.35 to 0.65 and 0.15 to 0.95
  **[PROVISIONAL]**.
- Spot check: 100 random positives per detector, verdicts reviewed
  by eye **[PROVISIONAL]**.

### Phase 0 gate (data audit, no model)

Phase 1 starts only if all hold. If one fails, the record says why
and the experiment stops.

| # | Criterion |
|---|-----------|
| G1 | Licence outcomes for both datasets are recorded above. |
| G2 | Negatives: every image on which either detector fires has been reviewed by eye, and a random sample of 200 of the rest has been reviewed. |
| G3 | If a face is found in the random sample, the whole negative set is reviewed. If more than 5% of negatives contain a face, the "no face" labelling is unreliable and the experiment stops **[PROVISIONAL]**. |
| G4 | At least 1000 positives and at least 1000 negatives remain in the test set (spec 3A.3). |
| G5 | Manifests are generated and checksummed, and size distributions are recorded. |
| G6 | Proxy ranges, the operating-point search spaces, the selection rule, and the budget below are committed before any metric is computed. |
| G7 | The pretrained-model fields below are complete for both detectors, including checksums. |

### Software and hardware

- Python: (to fill). PyTorch: (to fill).
- OpenCV: **opencv-contrib-python 5.0.0.93**, regular (not
  headless), not a rolling release. Exactly one OpenCV wheel may be
  installed in the environment.
- MTCNN: **facenet-pytorch 2.5.2**.
- All other packages are pinned in a lock file stored with this
  record. If the pins of facenet-pytorch conflict with OpenCV 5's
  requirements (for example NumPy), the conflict is resolved and
  recorded. Pins are not relaxed silently.
- Code commit, config file path: (to fill). Results from
  uncommitted code are invalid.
- Hardware: CPU model and cores, RAM, GPU (if used), OS: (to fill).
  The target hardware is undefined (spec Open Item 2), so latency is
  reported with the hardware used. MTCNN on CPU and, if used, on
  GPU are reported separately.
- Network: the experiment is run with network access disabled
  after installation, to confirm that nothing is downloaded at run
  time (constitution §3).
- Image decoding: each image is decoded once with one library. The
  conversion each detector needs (grayscale for the cascade, RGB for
  MTCNN) is applied explicitly and recorded.

## Model

Both detectors are pretrained and used frozen (no fine-tuning, no
employee data). Pretrained-model fields follow spec 2.2.

### Detector A: Haar cascade (OpenCV)

- **What:** `CascadeClassifier` with `haarcascade_frontalface_default.xml`,
  a stump-based 24 x 24 AdaBoost frontal-face cascade by Rainer
  Lienhart.
- **Source and version:** OpenCV 5.0.0.93, contrib build. In OpenCV
  5 the Haar `CascadeClassifier` moved from the core module to the
  contrib module `xobjdetect`, which is why the contrib wheel is
  required. Whether the XML file ships inside this wheel (for
  example under `cv2.data`) is to be confirmed. If not, obtain it
  from the OpenCV repository and record the URL.
- **File path, size, SHA-256, retrieval date:** (to fill).
- **Is it the file LFW's creators used?** LFW was built in 2007
  with this cascade name in OpenCV 1.0.0. Whether the file in this
  wheel is byte-identical is unknown. Record the checksum and, if the
  old file is obtainable, compare.
- **Licence:** the file header states the Intel License Agreement
  for the Open Source Computer Vision Library (copyright 2000).
  The wrapper package is Apache 2.0. Whether this allows the
  company's intended use: (owner to confirm).
- **Training data:** not stated in the file header. Treated as
  **undocumented**.
- **Leakage (spec 3A.7):** overlap with LFW or Singh's cannot be
  excluded from documentation. Marked **possible leakage**. Also,
  LFW's selection bias (spec 3A.8).
- **Employee data exposure:** none (frozen, never trained on
  employee data). Decision 0001 retraining does not apply.
- **Output:** boxes only, no confidence score, no landmarks.
  Ordering rule (spec 3A.1): largest box first.

### Detector B: MTCNN (facenet-pytorch)

- **What:** `facenet_pytorch.MTCNN`, a three-stage cascade (P-Net,
  R-Net, O-Net). Boxes come from `detect()` and are sorted by
  probability, highest first, by the experiment code. Landmarks are
  available but not used.
- **Source and version:** facenet-pytorch 2.5.2 (PyPI). Weights
  were ported from the TensorFlow `facenet` repository by David
  Sandberg, which implements the MTCNN of Zhang et al. (2016).
- **Weights files:** the package appears to ship `pnet.pt`,
  `rnet.pt`, and `onet.pt`. Confirm that they are present in the
  installed package and record each file's size and SHA-256:
  (to fill). The package's own licence is MIT.
- **Training data (original paper):** WIDER FACE (positives,
  negatives, part faces) and CelebA (landmark faces).
- **Licence of the training data:** listings I found describe both
  datasets as non-commercial or research-use. Whether that limits
  the company's use of weights trained on them is **unclear** and is
  a legal question. Recorded as a risk linked to constitution Open
  Item 9 (third-party consent) and Decision 0002.
- **Leakage (spec 3A.7):** no use of LFW is described, but CelebA
  and LFW both contain public figures from the web, and image-level
  overlap cannot be excluded from documentation. Marked **possible
  leakage**.
- **Employee data exposure:** none.
- **Output:** boxes with probabilities, optional landmarks.

### Consequence of the leakage marks

Under spec 3A.7, neither detector's result may be used to claim
that the targets are met. This experiment is therefore a
comparison and a calibration of the protocol, not adoption
evidence.

## Training strategy

n/a. Both detectors are pretrained and frozen. The look-up of
provenance, licence, and training data is in the Model section.

## Hyperparameters

Operating-point search (spec 3A.4). Both detectors get the same
budget: **12 configurations each [PROVISIONAL]**. Spaces and the
selection rule are frozen at G6.

**Haar cascade** (4 x 3 = 12):
- `minNeighbors`: 3, 5, 7, 9
- `scaleFactor`: 1.05, 1.1, 1.2
- `minSize`: fixed at (30, 30)

**MTCNN** (6 x 2 = 12):
- O-Net threshold: 0.5, 0.6, 0.7, 0.8, 0.9, 0.95
- pyramid `factor`: 0.709 (default), 0.8
- P-Net and R-Net thresholds fixed at 0.6 and 0.7
- `min_face_size` fixed at 20 (default)

**Selection rule**, applied on the evaluation set only:
1. Keep configurations that meet detection rate of at least 99%
   and false detection rate of at most 1% together.
2. Among them, pick the lowest false detection rate. Break ties by
   the highest detection rate, then by the lowest p50 latency.
3. If none qualifies, pick the smallest overshoot (spec 3A.4) and
   say so.

The default (untuned) settings of each detector are also run and
reported for information. The test set is used once per selected
configuration.

## Metrics

All on the test set, with 95% intervals (spec 3A.6: bootstrap over
identities for positives, over images for negatives):

- detection rate, no-detection rate, wrong-box rate;
- false detection rate;
- paired difference in detection rate (for H1);
- extra detections (information only);
- median relative box width of correct detections (information);
- latency p50 and p95, per class (positives, negatives), with image
  size distributions, hardware, warm-up (10 runs), and at least 200
  timed photos **[PROVISIONAL]**;
- brightness-stratified detection rate (information; strata under
  30 images flagged);
- results at the two sensitivity ranges; a conclusion that changes
  across the three ranges is marked fragile;
- proxy spot-check outcome (share of verdicts the reviewer
  disagrees with);
- size: XML file size for A, parameter count and file sizes for B;
- the operating point used for each detector.

Training time: n/a.

## Result

Two parts were planned: Phase 0 (audit outcomes, gates G1 to G7)
and Phase 1 (metrics above). **Neither was carried out as
specified.** Only a preliminary run was made, with the author's own
script, and it is recorded here as such. It deviates from spec 3A
and, under spec 3.8 and 2.1, MUST NOT be compared directly with
protocol-conforming results.

### Phase 0 (data audit)

Not performed.

| # | Status |
|---|--------|
| G1 | Not recorded here (the licence fields above are still "(to fill)"). |
| G2 | Not performed. The negatives were not reviewed by eye. |
| G3 | Not performed (depends on G2). |
| G4 | Not evaluated, because no split was made. Totals seen in the run: 13233 positives, 3983 negatives. |
| G5 | Not met. No manifests or checksums. |
| G6 | Not met. The run used neither the pre-registered proxy, nor the search spaces, nor the selection rule. |
| G7 | Not recorded. Paths, sizes and checksums of the pretrained files were not captured for this run. |

### Phase 1: preliminary run

Date and time of the results: **2026-10-25, 23:40** (as given by the
author; time zone not recorded).

How this run differs from the protocol (from the script used):

- **No split, no cap, no tuning.** All 13233 LFW original images
  and all 3983 negatives were evaluated together. There is no
  evaluation set, no test set, and no per-identity cap (3A.3).
- **One fixed setting per detector**, not the 12-configuration
  search. MTCNN: thresholds 0.6, 0.6, 0.7, `min_face_size` 30,
  `factor` 0.709, `device=None`. This is not a point of the
  registered grid (R-Net is 0.6 instead of 0.7, and `min_face_size`
  is 30 instead of 20). Haar: `scaleFactor` 1.1, `minNeighbors` 5,
  `minSize` (30, 30), which is a point of the registered grid.
- **Different correctness proxy.** A detection on a positive counted
  as correct if the centre of the top box was within 20 pixels of
  the image centre on both axes. The registered proxy (3A.4:
  the box contains the image centre, width between 0.25 and 0.85 of
  the image width) was not used, and no sensitivity ranges were run.
- **Negatives unreviewed.** Any detection on a negative counted as
  a false positive, with no check that the image has no face (G2).
- **Top box:** MTCNN's highest-probability box, Haar's largest box,
  as registered.
- **Conversions:** images decoded once with Pillow in RGB. Grayscale
  for the cascade was made with Pillow (`convert("L")`) inside the
  timed detector call.
- **No uncertainty:** no confidence intervals, no paired difference.
- **Not recorded:** hardware, software versions, code commit,
  config file, whether the network was disabled.

Counts and rates (positives n = 13233, negatives n = 3983):

| Metric | MTCNN | Haar cascade |
|--------|-------|--------------|
| False negatives (no detection or off-centre box, not separated) | 617 | 236 |
| False negative rate | 4.66% | 1.78% |
| Detection rate (1 minus false negative rate) | 95.34% | 98.22% |
| False positives (negatives with at least one detection) | 110 | 101 |
| False positive rate | 2.76% | 2.54% |
| Overall accuracy, 1 - (FP + FN) / 17216 | 95.78% | 98.04% |

Time (17216 photos, positives and negatives pooled, hardware not
recorded, no warm-up; MTCNN ran first, then Haar):

| Metric | MTCNN | Haar cascade |
|--------|-------|--------------|
| Total experiment time (loading, conversion, detection) | 147.76 s | 129.21 s |
| Total time in detector calls only | 140.44 s | 120.34 s |
| Mean per photo, total experiment time | 8.58 ms | 7.51 ms |
| Mean per photo, detector calls only | 8.16 ms | 6.99 ms |

Not available from this run: no-detection and wrong-box rates
separately, extra detections, box size, latency p50 and p95 per
class, brightness strata, the other two proxy ranges, spot check,
model sizes, per-image outputs.

## Interpretation

**This record makes no choice between the detectors.** The run
below is preliminary and does not follow the protocol (see Result),
so it is read as an indication only.

**Hypotheses.** None could be assessed as registered, because they
need selected operating points, intervals and p95 latency, and none
of these exist. Point estimates only:

| | Point estimates | Direction relative to the hypothesis |
|---|---|---|
| H1, detection rate | MTCNN 95.34%, Haar 98.22%. Difference (MTCNN minus Haar): -2.88 percentage points. | MTCNN is lower, the direction in which H1 can fail. Whether it does depends on an interval that was not computed. The record already says that H1 failing is inconclusive. |
| H2, false detections | MTCNN 2.76%, Haar 2.54%. Difference: +0.22 points (9 images out of 3983). | Haar is not higher, the direction in which H2 fails. No intervals. The negatives were not reviewed. |
| H3, latency | Detector calls only, mean: Haar 6.99 ms, MTCNN 8.16 ms (MTCNN +1.17 ms, about 17% more). | Haar lower, as H3 states. The p95 and the 500 ms limit were not measured, and positives and negatives were pooled. |

The expectation written in advance, that both detectors would score
near 100% on the positives, did not hold in this run (95.34% and
98.22%). This run cannot say whether the cause is the detectors, the
fixed settings, or the proxy (see below). Under the outcome table
fixed in advance, "Haar ahead on detection rate" is read as
**inconclusive (selection bias)**. The row "MTCNN at least equal on
detection rate and lower on false detections" does not apply.

**Known biases (spec 3A.8) and how each may have affected this run.**

1. *Selection bias toward Haar.* Every positive is a face that a
   Haar-based Viola-Jones detector found. The direction of the
   detection-rate difference is the one this bias predicts. It must
   not be read as evidence that Haar is better.
2. *Ceiling effect, no scale variation.* Not a limit here, since
   neither detector is near 100%. Robustness to face size is still
   untested, because the faces have nearly constant size.
3. *No ground-truth boxes.* The 20 pixel centre criterion compares
   the box centre with the image centre. LFW images are centred on a
   Haar box enlarged by about 2.2 (3A.4), so the criterion may favour
   Haar's box convention. If MTCNN's boxes are centred differently,
   part of its 617 false negatives could be proxy artefacts rather
   than misses. This run cannot tell: no-detection and wrong-box were
   not counted separately and no spot check was done.
4. *Easy negatives and no review.* The negatives are object photos,
   so a false positive rate of 2.5% to 2.8% is not small. Some of
   the 110 and 101 detections may be real faces in the negatives (G2
   was not done), which would count as false positives here without
   being detector errors. Whether the two detectors fired on the same
   images is unknown, since per-image outputs were not saved.
5. *Not entrance conditions.* Nothing here describes the entrance
   camera (spec Open Item 4).

Two further limits. The positives were not capped, and the protocol
caps them because a few identities have hundreds of images; the
rates are therefore weighted toward those identities, and
uncertainty by identity was not computed. Accuracy is also weighted
by the class mix (13233 positives to 3983 negatives) and is not
comparable with results on other mixes.

**Leakage.** Both detectors keep the mark **possible leakage**
(spec 3A.7). The Haar cascade's training data is undocumented. For
MTCNN, overlap between CelebA or WIDER FACE and LFW cannot be
excluded from documentation.

**Targets.** Neither detector's point estimate reaches the
provisional detection rate of 99% or false detection rate of 1%
under this run's settings and proxy. Because the settings were not
tuned, this does not show whether any setting in the registered
search spaces would reach them. Because of the leakage marks, the
biases above and the preliminary nature of the run, no target result
here, met or missed, is evidence of entrance performance.

**What this feeds.** No detector is chosen for the next modules.
Whether the gap in detection rate belongs to the detectors or to the
data and the proxy cannot be told from this run, which bears on
spec Open Item 8 (a second detection dataset, free of LFW's
Viola-Jones selection and with boxes) and on spec Open Item 9
(detector adoption criteria). To move this record to `done`, Phase 0
(G1 to G7) and a Phase 1 run with the split, the search and the
metrics above are still needed, and this preliminary run is to be
kept as a recorded deviation.

How to read the outcomes, fixed in advance:

| Outcome | Reading |
|---------|---------|
| MTCNN at least equal on detection rate and lower on false detections | Supports MTCNN. Meaningful, since the data favors Haar on detection. |
| Haar ahead on detection rate | Inconclusive (selection bias). |
| Both near 100% with overlapping intervals | No separation on detection rate. Decide on false detections and latency, with the caveats above. |
| Conclusion changes across the proxy ranges | Fragile. Do not rely on it. |
