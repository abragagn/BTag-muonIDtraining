#!/bin/sh
#BSUB -o testBarrel.log
eval `scram runtime -sh`
python trainingGlobal2017.py Barrel woIP wIso
