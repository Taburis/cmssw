#include "RecoHI/HiTracking/interface/HIBestVertexProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include <algorithm>
#include <iostream>
using namespace std;
using namespace edm;

/*****************************************************************************/
HIBestVertexProducer::HIBestVertexProducer
(const edm::ParameterSet& ps) : theConfig(ps),
  theBeamSpotTag(consumes<reco::BeamSpot>(ps.getParameter<edm::InputTag>("beamSpotLabel"))),
  theMedianVertexCollection(consumes<reco::VertexCollection>(ps.getParameter<edm::InputTag>("medianVertexCollection"))),
  theAdaptiveVertexCollection(consumes<reco::VertexCollection>(ps.getParameter<edm::InputTag>("adaptiveVertexCollection")))
{
  theUseFinalAdapativeVertexCollection  = (ps.existsAs<bool>("useFinalAdapativeVertexCollection") ? ps.getParameter<bool>("useFinalAdapativeVertexCollection") : false);
  if(theUseFinalAdapativeVertexCollection) theFinalAdaptiveVertexCollection = consumes<reco::VertexCollection>(ps.getParameter<edm::InputTag>("finalAdaptiveVertexCollection"));
  produces<reco::VertexCollection>();
}


/*****************************************************************************/
HIBestVertexProducer::~HIBestVertexProducer()
{ 
}

/*****************************************************************************/
void HIBestVertexProducer::beginJob()
{
}

/*****************************************************************************/
void HIBestVertexProducer::produce
(edm::Event& ev, const edm::EventSetup& es)
{
  
  // 1. use best adaptive vertex preferentially
  // 2. use median vertex in case where adaptive algorithm failed
  // 3. use beamspot if netither vertexing method succeeds

  // New vertex collection
  auto newVertexCollection = std::make_unique<reco::VertexCollection>();

  //** Get precise adaptive vertex **/
  edm::Handle<reco::VertexCollection> vc1;
  ev.getByToken(theAdaptiveVertexCollection, vc1);
  const reco::VertexCollection *vertices1 = vc1.product();

  if(vertices1->size()==0)
    LogError("HeavyIonVertexing") << "adaptive vertex collection is empty!" << endl;

  //** Final vertex collection if needed **//
  bool hasFinalVertex = false;
  if(theUseFinalAdapativeVertexCollection){
    edm::Handle<reco::VertexCollection> vc0;
    ev.getByToken(theFinalAdaptiveVertexCollection, vc0);
    const reco::VertexCollection *vertices0 = vc0.product();
    if(vertices0->size()==0)
      LogError("HeavyIonVertexing") << "final adaptive vertex collection is empty!" << endl;
  
    //if using final vertex and has a good vertex and it has more tracks than pixel track adaptive vertex, use it
    if(vertices0->begin()->zError()<3){
      hasFinalVertex = true;
      reco::VertexCollection::const_iterator vertex0 = vertices0->begin();
      newVertexCollection->push_back(*vertex0);
      LogInfo("HeavyIonVertexing") << "adaptive vertex:\n vz = (" 
				 << vertex0->x() << ", " << vertex0->y() << ", " << vertex0->z() << ")" 
				 << "\n error = ("
				 << vertex0->xError() << ", " << vertex0->yError() << ", " 
				 << vertex0->zError() << ")" << endl;
    }
  }

  //otherwise use the pixel track adaptive vertex if it is good
  if(!hasFinalVertex){
    if(vertices1->begin()->zError()<3) { 
    
      reco::VertexCollection::const_iterator vertex1 = vertices1->begin();
      newVertexCollection->push_back(*vertex1);
  
      LogInfo("HeavyIonVertexing") << "adaptive vertex:\n vz = (" 
  				 << vertex1->x() << ", " << vertex1->y() << ", " << vertex1->z() << ")" 
  				 << "\n error = ("
  				 << vertex1->xError() << ", " << vertex1->yError() << ", " 
  				 << vertex1->zError() << ")" << endl;
    //otherwise use fast vertex or beamspot
    } else {
      
      //** Get fast median vertex **/
      edm::Handle<reco::VertexCollection> vc2;
      ev.getByToken(theMedianVertexCollection, vc2);
      const reco::VertexCollection * vertices2 = vc2.product();
      
      //** Get beam spot position and error **/
      reco::BeamSpot beamSpot;
      edm::Handle<reco::BeamSpot> beamSpotHandle;
      ev.getByToken(theBeamSpotTag, beamSpotHandle);
  
      if( beamSpotHandle.isValid() ) 
        beamSpot = *beamSpotHandle;
      else
        LogError("HeavyIonVertexing") << "no beamspot found "  << endl;
  
      if(vertices2->size() > 0) { 
        
        reco::VertexCollection::const_iterator vertex2 = vertices2->begin();
        reco::Vertex::Error err;
        err(0,0)=pow(beamSpot.BeamWidthX(),2);
        err(1,1)=pow(beamSpot.BeamWidthY(),2);
        err(2,2)=pow(vertex2->zError(),2);
        reco::Vertex newVertex(reco::Vertex::Point(beamSpot.x0(),beamSpot.y0(),vertex2->z()),
  			     err, 0, 1, 1);
        newVertexCollection->push_back(newVertex);  
  
        LogInfo("HeavyIonVertexing") << "median vertex + beamspot: \n position = (" 
  				   << newVertex.x() << ", " << newVertex.y() << ", " << newVertex.z() << ")" 
  				   << "\n error = ("
  				   << newVertex.xError() << ", " << newVertex.yError() << ", " 
  				   << newVertex.zError() << ")" << endl;
        
      } else { 
        
        reco::Vertex::Error err;
        err(0,0)=pow(beamSpot.BeamWidthX(),2);
        err(1,1)=pow(beamSpot.BeamWidthY(),2);
        err(2,2)=pow(beamSpot.sigmaZ(),2);
        reco::Vertex newVertex(beamSpot.position(), 
  			     err, 0, 0, 1);
        newVertexCollection->push_back(newVertex);  
  
        LogInfo("HeavyIonVertexing") << "beam spot: \n position = (" 
  				   << newVertex.x() << ", " << newVertex.y() << ", " << newVertex.z() << ")" 
  				   << "\n error = ("
  				   << newVertex.xError() << ", " << newVertex.yError() << ", " 
  				   << newVertex.zError() << ")" << endl;
        
      }
      
    }
  }
  
  // put new vertex collection into event
  ev.put(std::move(newVertexCollection));
  
}

