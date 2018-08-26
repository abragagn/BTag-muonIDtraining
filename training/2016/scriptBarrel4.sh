#!/bin/sh
#BSUB -o testBarrel4.log
eval `scram runtime -sh`
python trainingGlobal2016.py Barrel woIP woIso
