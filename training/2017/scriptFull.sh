#!/bin/sh
#BSUB -o testFull.log
eval `scram runtime -sh`
python trainingGlobal2017.py Full woIP wIso
