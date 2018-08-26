#!/bin/sh
#BSUB -o testEndcap.log
eval `scram runtime -sh`
python trainingGlobal2016.py Endcap wIP wIso
