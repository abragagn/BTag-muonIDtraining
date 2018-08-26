#!/bin/sh
#BSUB -o testEndcap4.log
eval `scram runtime -sh`
python trainingGlobal2017.py Endcap woIP woIso
