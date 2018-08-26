#!/bin/sh
#BSUB -o testBarrel2.log
eval `scram runtime -sh`
python trainingGlobal2017.py Barrel woIP wIso
