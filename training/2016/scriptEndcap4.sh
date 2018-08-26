#!/bin/sh
#BSUB -o testEndcap4.log
eval `scram runtime -sh`
python trainingGlobal2016.py Endcap woIP woIso
