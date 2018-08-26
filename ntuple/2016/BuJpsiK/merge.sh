#!/bin/bash
i=0;
max=1;
echo $'#!/bin/sh' > park.sh
echo -n "hadd bankBuJpsiK16.root" >> park.sh
while [ "$i" -le "$max" ]; do
  echo -n " s$i/ntu$i" >> park.sh
  echo -n ".root" >> park.sh
  i=`expr "$i" + 1`;
done
echo " " >> park.sh
bash park.sh;
rm park.sh;
mv ./bankBuJpsiK16.root /lustre/cmswork/abragagn/BPH/MuonID/muonIDtraining/src/PDAnalysis/Ntu/bin/training/2016/
