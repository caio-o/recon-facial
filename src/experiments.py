#!/bin/python3
import os
import numpy as np
import facenet_pytorch
from facenet_pytorch import MTCNN, InceptionResnetV1
import classes
from PIL import Image

def main():
    CLASSES_DIR = "../data/public/lfw/lfw-deepfunneled"
    print("Beginning experiments.")

    print("Loading classes...")
    clss = classes.load_classes(CLASSES_DIR)
    print(f"Classes: {clss}")
    
    print("Loading photos...")
    photos = classes.load_photos(CLASSES_DIR, clss)
    print("Photos for Leonardo DiCaprio:", photos["Leonardo_DiCaprio"])

    print("End of experiments.")

main()

