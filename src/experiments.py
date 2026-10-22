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
    print("Photos for Leonardo DiCaprio:", photos["Lula"])

    print("Preprocessing Lula 1", photos["Lula"][0])
    im = preprocess.load_preprocessed(photos["Lula"][0])
    im.show()

    print("Preprocessing Lula 2", photos["Lula"][1])
    im = preprocess.load_preprocessed(photos["Lula"][1])
    im.show()

    print("Preprocessing Lula 3", photos["Lula"][2])
    im = preprocess.load_preprocessed(photos["Lula"][2])
    im.show()

    print("End of experiments.")

main()

