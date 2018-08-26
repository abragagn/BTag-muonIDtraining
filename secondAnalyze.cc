//#define UTIL_USE FULL
//#include "PDAnalyzer.h"
//#include "NtuAnalysis/Read/interface/NtuFlexibleAnalyzer.h"
//#include "NtuTool/Read/bin/treeAnalyze.cc"
//static NtuFlexibleAnalyzer<PDSecondAnalyzer> nfa( "pdAnalysis", "pdAnalyzer" );
#include "PDSecondNtupleReader.h"
#include "PDSecondNtupleReader.cc"
#include "NtuTool/Read/bin/treeAnalyze.cc"
static PDSecondNtupleReader snr;
