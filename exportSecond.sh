#!/bin/sh

cd `dirname $0`/../../..
export PD_PATH=PDAnalysis/Ntu
export PD_PACK=`pwd`/pdAnalysisSecond.tgz
rm -f ${PD_PACK}
tar -czf ${PD_PACK}                    \
${PD_PATH}/bin/PDSecondNtupleData.*    \
${PD_PATH}/bin/PDSecondNtupleReader.*  \
${PD_PATH}/bin/secondAnalyze.cc        \
${PD_PATH}/bin/compileSecondEX.sh      \
${PD_PATH}/bin/exportSecond.sh
#
#${PD_PATH}/bin/*.cc                    \
#${PD_PATH}/bin/compile.sh              \
#${PD_PATH}/bin/*Macro.C                \
#${PD_PATH}/bin/*Proof.mac              \
#${PD_PATH}/bin/setupMacroAnalysis.sh   \
#${PD_PATH}/bin/installProofAnalysis.sh \
#${PD_PATH}/bin/*_test.list             \
echo ${PD_PACK}
