#!/bin/bash
i=0;
max=3;
echo $'#!/bin/sh' > park.sh
echo -n "hadd bankBsJpsiPhiDGamma017.root" >> park.sh
while [ "$i" -le "$max" ]; do
  echo -n " s$i/ntu$i" >> park.sh
  echo -n ".root" >> park.sh
  i=`expr "$i" + 1`;
done
echo " " >> park.sh
bash park.sh;
rm park.sh;
mv ./bankBsJpsiPhiDGamma017.root ../
