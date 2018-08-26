#!/bin/bash
i=0;
max=100;
n=1000000;
while [ "$i" -le "$max" ]; do
  mkdir "s$i";
  cd "s$i";
  skip=$(python -c "print 0+$n*$i");
  echo $'#!/bin/sh' > script.sh
  echo $'#BSUB -o testBs.log' >> script.sh
  echo $'eval `scram runtime -sh`' >> script.sh
  echo "pdTreeAnalyze /lustre/cmswork/abragagn/ntuList/MC2016Lists/BsToJpsiPhi_BMuonFilter_2016_DCAP.list hist$i.root -v outputFile ntu$i.root -v histoMode RECREATE -v use_gen t -v process BsJPsiPhi -n $n -s $skip" >> script.sh
  echo "" >> script.sh
  bsub < script.sh;
  cd ..;
  i=`expr "$i" + 1`;
done
