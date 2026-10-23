#!/bin/python3
import os
import numpy as np
import facenet_pytorch
from facenet_pytorch import MTCNN, InceptionResnetV1
import classes
import preprocess
from PIL import Image

def main():
    CLASSES_DIR = "../data/public/lfw/lfw-deepfunneled"
    print("Beginning experiments.")

    print("Loading classes...")
    clss = classes.load_classes(CLASSES_DIR)
    print(f"Classes: {clss}")
    
    print("Loading photos...")
    photos = classes.load_photos(CLASSES_DIR, clss)
    
    successes = []
    faces_not_found = []

    for lst in photos.values():
        for photo in lst:
            try:
                preprocess.load_preprocessed(photo)
                successes.append(photo)
            except ValueError:
                faces_not_found.append(photo)

    print('Faces found: ', len(successes))
    print('Faces not found: ', len(faces_not_found))
    print('List of photos where no face was found:')
    for photo in faces_not_found:
        print(photo)

    print("End of experiments.")

main()

