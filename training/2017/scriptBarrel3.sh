#!/bin/sh
#BSUB -o testBarrel3.log
eval `scram runtime -sh`
python trainingGlobal2017.py Barrel wIP woIso
