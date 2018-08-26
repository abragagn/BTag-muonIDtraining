#!/bin/sh
#BSUB -o testEndcap2.log
eval `scram runtime -sh`
python trainingGlobal2016.py Endcap woIP wIso
