#!/bin/bash
i=0;
max=100;
echo $'#!/bin/sh' > park.sh
echo -n "hadd bankBsJpsiPhi16.root" >> park.sh
while [ "$i" -le "$max" ]; do
  echo -n " s$i/ntu$i" >> park.sh
  echo -n ".root" >> park.sh
  i=`expr "$i" + 1`;
done
echo " " >> park.sh
bash park.sh;
rm park.sh;
mv ./bankBsJpsiPhi16.root /lustre/cmswork/abragagn/BPH/MuonID/muonIDtraining/src/PDAnalysis/Ntu/bin/training/2016/
