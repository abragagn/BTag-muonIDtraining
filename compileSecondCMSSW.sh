#!/bin/sh

cd `dirname $0`/..
export PD_PACK_DIR=`/bin/pwd`
cd ../..
export PD_ROOT_DIR=`/bin/pwd`
echo ${PD_PACK_DIR}
echo ${PD_ROOT_DIR}

export PD_EXE_FILE=${PD_PACK_DIR}/bin/secondTreeAnalyze
rm -f ${PD_EXE_FILE}

c++ -Wall `root-config --cflags`              \
-I ${PD_ROOT_DIR}                             \
-o ${PD_EXE_FILE}                             \
${PD_PACK_DIR}/bin/secondAnalyze.cc           \
-L${CMSSW_BASE}/lib/${SCRAM_ARCH}             \
-lNtuToolCommon -lNtuToolRead `root-config --glibs`
