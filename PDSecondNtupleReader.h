#ifndef PDSecondNtupleReader_h
#define PDSecondNtupleReader_h

#include "PDSecondNtupleData.h"
#include "NtuTool/Read/interface/TreeReader.h"
#include "TFile.h"
#include "TH1.h"
#include <string>
#include <iostream>

class PDSecondNtupleReader: public PDSecondNtupleData, public TreeReader {

 public:

  PDSecondNtupleReader() {}
  virtual ~PDSecondNtupleReader() {}

  virtual void beginJob() {
    initTree();
  }

  virtual void book() {
    autoSavedObject =
      hSum = new TH1F( "hSum", "hSum", 10, -0.5, 9.5 );
    autoSavedObject =
      hPro = new TH1F( "hPro", "hPro", 10, -0.5, 9.5 );
  }
  virtual bool analyze( int entry, int event_file, int event_tot ) {
    hSum->Fill( nSum );
    hPro->Fill( nPro );
    return true;
  }
  virtual void endJob() {}

 private:

  TH1F* hSum;
  TH1F* hPro;

  PDSecondNtupleReader           ( const PDSecondNtupleReader& a );
  PDSecondNtupleReader& operator=( const PDSecondNtupleReader& a );

};

#endif

