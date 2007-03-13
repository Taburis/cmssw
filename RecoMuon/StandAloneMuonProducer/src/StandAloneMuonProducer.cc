/**  \class StandAloneMuonProducer
 * 
 *   StandAlone muon reconstructor:
 *   reconstructs muons using DT, CSC and RPC
 *   information,<BR>
 *   starting from internal seeds (L2 muon track segments).
 *
 *
 *   $Date: 2007/03/07 13:20:56 $
 *   $Revision: 1.24 $
 *
 *   \author  R.Bellan - INFN TO
 */

// Framework
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "RecoMuon/StandAloneMuonProducer/src/StandAloneMuonProducer.h"

// TrackFinder and Specific STA Trajectory Builder
#include "RecoMuon/StandAloneTrackFinder/interface/StandAloneTrajectoryBuilder.h"
#include "RecoMuon/TrackingTools/interface/MuonTrackFinder.h"
#include "RecoMuon/TrackingTools/interface/MuonTrackLoader.h"
#include "RecoMuon/TrackingTools/interface/MuonServiceProxy.h"

// Input and output collection

#include "DataFormats/TrajectorySeed/interface/TrajectorySeedCollection.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackToTrackMap.h"

#include <string>

using namespace edm;
using namespace std;

/// constructor with config
StandAloneMuonProducer::StandAloneMuonProducer(const ParameterSet& parameterSet){
  LogTrace("Muon|RecoMuon|StandAloneMuonProducer")<<"constructor called"<<endl;

  // Parameter set for the Builder
  ParameterSet trajectoryBuilderParameters = parameterSet.getParameter<ParameterSet>("STATrajBuilderParameters");
  
  // MuonSeed Collection Label
  theSeedCollectionLabel = parameterSet.getParameter<InputTag>("InputObjects");
  
  // service parameters
  ParameterSet serviceParameters = parameterSet.getParameter<ParameterSet>("ServiceParameters");
  
  // TrackLoader parameters
  ParameterSet trackLoaderParameters = parameterSet.getParameter<ParameterSet>("TrackLoaderParameters");
  
  // the services
  theService = new MuonServiceProxy(serviceParameters);

  // instantiate the concrete trajectory builder in the Track Finder
  theTrackFinder = new MuonTrackFinder(new StandAloneMuonTrajectoryBuilder(trajectoryBuilderParameters,theService),
				       new MuonTrackLoader(trackLoaderParameters,theService));
  
  produces<reco::TrackCollection>();
  produces<reco::TrackCollection>("UpdatedAtVtx");
  produces<TrackingRecHitCollection>();
  produces<reco::TrackExtraCollection>();
  produces<reco::TrackToTrackMap>();
  
  produces<std::vector<Trajectory> >();
}
  
/// destructor
StandAloneMuonProducer::~StandAloneMuonProducer(){
  LogTrace("Muon|RecoMuon|StandAloneMuonProducer")<<"StandAloneMuonProducer destructor called"<<endl;
  if (theService) delete theService;
  if (theTrackFinder) delete theTrackFinder;
}

/// reconstruct muons
void StandAloneMuonProducer::produce(Event& event, const EventSetup& eventSetup){
  const std::string metname = "Muon|RecoMuon|StandAloneMuonProducer";
  
  LogTrace(metname)<<endl<<endl<<endl;
  LogTrace(metname)<<"Stand Alone Muon Reconstruction Started"<<endl;

  // Take the seeds container
  LogTrace(metname)<<"Taking the seeds: "<<theSeedCollectionLabel.label()<<endl;
  Handle<TrajectorySeedCollection> seeds; 
  event.getByLabel(theSeedCollectionLabel,seeds);

  // Update the services
  theService->update(eventSetup);

  // Reconstruct 
  LogTrace(metname)<<"Track Reconstruction"<<endl;
  theTrackFinder->reconstruct(seeds,event);
 
  LogTrace(metname)<<"Event loaded"
		   <<"================================"
		   <<endl<<endl;
}

