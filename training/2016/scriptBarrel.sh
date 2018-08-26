#!/bin/sh
#BSUB -o testBarrel.log
eval `scram runtime -sh`
python trainingGlobal2016.py Barrel wIP wIso
