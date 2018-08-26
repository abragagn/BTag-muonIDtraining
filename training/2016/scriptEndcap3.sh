#!/bin/sh
#BSUB -o testEndcap3.log
eval `scram runtime -sh`
python trainingGlobal2016.py Endcap wIP woIso
