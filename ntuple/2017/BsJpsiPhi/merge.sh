#!/bin/bash
i=0;
max=10;
echo $'#!/bin/sh' > park.sh
echo -n "hadd bankBsJpsiPhi17.root" >> park.sh
while [ "$i" -le "$max" ]; do
  echo -n " s$i/ntu$i" >> park.sh
  echo -n ".root" >> park.sh
  i=`expr "$i" + 1`;
done
echo " " >> park.sh
bash park.sh;
rm park.sh;
mv ./bankBsJpsiPhi17.root /lustre/cmswork/abragagn/BPH/MuonID/CMSSW_10_3_0_pre1/src/2017/
