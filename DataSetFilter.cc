
#include "DataSetFilter.h"

#include "PDAnalysis/Ntu/interface/PDEnumString.h"

#include <iostream>


DataSetFilter::DataSetFilter():
 eventCount( false ),
 nReadEvts( 0 ),
 nAccepted( 0 ) {
  nTrig = PDEnumString::DUMMY_LAST_TRIGGER;
  triggerReq = new bool[nTrig];
  triggerRej = new bool[nTrig];
//  triggerJoin = new int[nTrig];
  triggerJoin = new std::vector<int>[nTrig];
  int iTrig;
  for ( iTrig = 0; iTrig < nTrig; ++iTrig ) {
    triggerReq[iTrig] =
    triggerRej[iTrig] = false;
    triggerJoin[iTrig].reserve( nTrig );
  }
}


DataSetFilter::~DataSetFilter() {
  delete[] triggerReq;
  delete[] triggerRej;
  delete[] triggerJoin;
}


void DataSetFilter::beginJob() {

  int iTrig;
  int jTrig;
  for ( iTrig = 0; iTrig < nTrig; ++iTrig ) {
    const std::string& request =
                       getUserParameter( PDEnumString::findTrigPath( iTrig ) );
//    triggerJoin[iTrig] = PDEnumString::DUMMY_LAST_TRIGGER;
    std::vector<int>& tj = triggerJoin[iTrig];
    if ( request != "" ) eventCount = true;
    if ( request.substr( 0, 3 ) == "OR_" ) {
//      triggerJoin[iTrig] = PDEnumString::findTrigPath( request.substr( 3,
//                                                       request.length() ) );
      jTrig = PDEnumString::findTrigPath( request.substr( 3,
                                          request.length() ) );
      tj.push_back( jTrig );
      triggerJoin[jTrig].push_back( iTrig );
    };
    triggerReq[iTrig] = ( request == "require" );
    triggerRej[iTrig] = ( request == "reject"  );
  }
  return;

}


bool DataSetFilter::triggerAccept() {

  ++nReadEvts;

  int iHLTStatus;
  int iTrig;
  bool aTrig[nTrig];
  for ( iTrig = 0; iTrig < nTrig; ++iTrig )
        aTrig[iTrig] = false;
  for ( iHLTStatus = 0; iHLTStatus < nHLTStatus; ++iHLTStatus )
        aTrig[hltPath->at( iHLTStatus )] = hltAccept->at( iHLTStatus );
  for ( iTrig = 0; iTrig < nTrig; ++iTrig ) {
  }
  for ( iTrig = 0; iTrig < nTrig; ++iTrig ) {
//    if ( triggerJoin[iTrig] < PDEnumString::DUMMY_LAST_TRIGGER ) {
//      if ( aTrig[triggerJoin[iTrig]] ) aTrig[            iTrig ] = true;
//      if ( aTrig[            iTrig]  ) aTrig[triggerJoin[iTrig]] = true;
//    }
    const std::vector<int>& tj = triggerJoin[iTrig];
    int iJoin;
    int nJoin = tj.size();
    for ( iJoin = 0; iJoin < nJoin; ++iJoin ) {
      if ( aTrig[tj[iJoin]] ) aTrig[   iTrig ] = true;
      if ( aTrig[   iTrig]  ) aTrig[tj[iJoin]] = true;
    }
  }
  for ( iTrig = 0; iTrig < nTrig; ++iTrig ) {
    if ( triggerReq[iTrig] && !aTrig[iTrig] ) return false;
    if ( triggerRej[iTrig] &&  aTrig[iTrig] ) return false;
  }
  ++nAccepted;
  return true;

}


void DataSetFilter::endJob() {
  if ( eventCount ) std::cout << nReadEvts << " events read, "
                              << nAccepted << " triggered" << std::endl;
  return;
}

