#ifndef DataSetFilter_H
#define DataSetFilter_H

#include "PDAnalyzerUtil.h"
#include <vector>

class DataSetFilter: public virtual PDAnalyzerUtil {

 public:

  DataSetFilter();
  virtual ~DataSetFilter();

 protected:

  // function called before starting the analysis
  virtual void beginJob();

  // accept or reject event according to trigger and dataset
  virtual bool triggerAccept();

  // function called at the end of the analysis
  virtual void endJob();

 private:

  int nTrig;
  bool* triggerReq;
  bool* triggerRej;
//  int* triggerJoin;
  std::vector<int>* triggerJoin;

  bool eventCount;
  int nReadEvts;
  int nAccepted;

  // dummy copy and assignment constructors
  DataSetFilter( const DataSetFilter& );
  DataSetFilter& operator=( const DataSetFilter& );

};


#endif

