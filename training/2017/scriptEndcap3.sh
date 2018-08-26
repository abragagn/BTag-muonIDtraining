#!/bin/sh
#BSUB -o testEndcap3.log
eval `scram runtime -sh`
python trainingGlobal2017.py Endcap wIP woIso
