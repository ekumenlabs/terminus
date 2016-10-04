#!/bin/sh

PYTHONPATH=$PYTHONPATH:.:./terminus python -m unittest discover -s ./terminus/tests -p '*_test.py'
