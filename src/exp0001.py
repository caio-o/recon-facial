import os
import time
import numpy as np
import PIL
import cv2
import facenet_pytorch
from facenet_pytorch import MTCNN
from preprocess import _load_cascade
import classes

POSITIVES_DIR = os.path.abspath("../data/public/lfw/lfw-original")
NEGATIVES_DIR = os.path.abspath("../data/public/.objects")

"""
    Configures and returns Facenet's MTCNN model and CV's Haar Cascade
"""
def get_models() -> {MTCNN, cv2.CascadeClassifier}:
    mtcnn = MTCNN(
        image_size=160,
        margin=0,
        min_face_size=30,
        thresholds=[0.6, 0.6, 0.7],
        factor=0.709,
        post_process=True,
        select_largest=True,
        keep_all=False,
        device=None
    )

    cascade = _load_cascade()

    return mtcnn, cascade
    
def get_positives():
    cls = classes.load_classes(POSITIVES_DIR)
    return classes.load_photos(POSITIVES_DIR, cls)

def get_negatives():
    cls = classes.load_classes(NEGATIVES_DIR)
    return classes.load_photos(NEGATIVES_DIR, cls)

"""
    True if the center of <box> (x1, y1, x2, y2) is within 20 pixels
    of the center of a <w> x <h> image, on both axes.
"""
def centered(w:int, h:int, box)->bool:
    res = False
    img_center = [w/2, h/2]
    box_center = [(box[0] + box[2])/2, (box[1] + box[3])/2]
    if abs(img_center[0] - box_center[0]) <= 20 \
        and abs(img_center[1] - box_center[1]) <= 20:
        res = True
    return res

"""
    Detector adapters. Each takes a PIL RGB image and returns the top
    box as (x1, y1, x2, y2), or None if nothing was detected.
"""
def mtcnn_detect(mtcnn: MTCNN, im):
    boxes, probs = mtcnn.detect(im)
    if boxes is not None \
        and boxes.size > 0:
        """ detect() sorts by probability, so boxes[0] is the top one. """
        return boxes[0]
    return None

def cv_hc_detect(cv2_hc: cv2.CascadeClassifier, im):
    gray = np.asarray(im.convert("L"))
    faces = cv2_hc.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    if len(faces) == 0:
        return None
    """ No score: keep the largest box. Convert (x, y, w, h) to corners. """
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return (x, y, x + w, y + h)

"""
    Runs <detect> over every photo and fills the results dict.
    On a positive, no detection or an off-center box is a false
    negative. On a negative, any detection is a false positive.
    Times are in seconds: "time_length" covers the whole experiment
    (image loading included), "detect_time" only the detector calls.
"""
def run_experiment(detect, positives: dict, negatives: dict)->dict:
    results   =  dict()
    im        =  None
    box       =  None
    t         =  None

    results["start_time"]       =  0
    results["finish_time"]      =  0
    results["time_length"]      =  0
    results["detect_time"]      =  0
    results["exp_size"]         =  0
    results["n_positives"]      =  0
    results["n_negatives"]      =  0
    results["avg_time"]         =  0
    results["avg_detect_time"]  =  0
    results["false_positives"]  =  0
    results["false_negatives"]  =  0
    results["fp_rate"]          =  0
    results["fn_rate"]          =  0
    results["accuracy"]         =  0

    results["start_time"] = time.perf_counter()

    """ Each value in <positives.values()> is a list of paths to photos containing faces. """
    for pos_list in positives.values():
        results["n_positives"] += len(pos_list)
        for pos in pos_list:

            """ Load image """
            im = PIL.Image.open(pos).convert("RGB")

            """ Apply the detector """
            t = time.perf_counter()
            box = detect(im)
            results["detect_time"] += time.perf_counter() - t

            if box is None \
                or not centered(im.width, im.height, box):
                results["false_negatives"] += 1

    for neg_list in negatives.values():
        results["n_negatives"] += len(neg_list)
        for neg in neg_list:
            """ Load image """
            im = PIL.Image.open(neg).convert("RGB")

            """ Apply the detector """
            t = time.perf_counter()
            box = detect(im)
            results["detect_time"] += time.perf_counter() - t

            if box is not None:
                results["false_positives"] += 1

    results["finish_time"] = time.perf_counter()
    results["time_length"] = results["finish_time"] - results["start_time"]
    results["exp_size"] = results["n_positives"] + results["n_negatives"]
    results["avg_time"] = results["time_length"] / results["exp_size"]
    results["avg_detect_time"] = results["detect_time"] / results["exp_size"]
    results["fp_rate"] = results["false_positives"] / results["n_negatives"]
    results["fn_rate"] = results["false_negatives"] / results["n_positives"]
    results["accuracy"] = 1 - (results["false_positives"] \
        + results["false_negatives"]) / results["exp_size"]

    return results

def mtcnn_experiment(mtcnn: MTCNN, positives: dict, negatives: dict)->dict:
    return run_experiment(lambda im: mtcnn_detect(mtcnn, im), \
        positives, negatives)

def cv_hc_experiment(cv2_hc: cv2.CascadeClassifier, \
    positives: dict, negatives: dict)->dict:
    return run_experiment(lambda im: cv_hc_detect(cv2_hc, im), \
        positives, negatives)

def exp_0001_main():
    mtcnn, cascade = get_models()
    positives = get_positives()
    negatives = get_negatives()
    mtcnn_results = mtcnn_experiment(mtcnn, positives, negatives)
    cv_hc_results = cv_hc_experiment(cascade, positives, negatives)
   
    print("Results for the MTCNN experiment: ")
    print(mtcnn_results) 
    print("Results for the Haar Cascade experiment: ")
    print(cv_hc_results)

exp_0001_main()
