#!/bin/sh
#BSUB -o testBarrel2.log
eval `scram runtime -sh`
python trainingGlobal2016.py Barrel woIP wIso
