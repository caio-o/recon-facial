#!/bin/python3
import argparse

def my_parse_args():
    parser = argparse.ArgumentParser
    
    parser.add_argument("--test", 
        help="Run all the tests.", 
        action="store_true")

    parser.add_argument("--version",
        help="Display version and exit.",
        action="store_true")

    args = parser.parse_args()

    return args

def main():
    args = my_parse_args()

    

