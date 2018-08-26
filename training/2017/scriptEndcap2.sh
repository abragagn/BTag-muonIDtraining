#!/bin/sh
#BSUB -o testEndcap2.log
eval `scram runtime -sh`
python trainingGlobal2017.py Endcap woIP wIso
