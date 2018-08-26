#!/bin/sh
#BSUB -o testEndcap.log
eval `scram runtime -sh`
python trainingGlobal2017.py Endcap wIP wIso
