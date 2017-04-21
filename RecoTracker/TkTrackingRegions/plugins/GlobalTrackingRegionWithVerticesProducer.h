#ifndef RecoTracker_TkTrackingRegions_GlobalTrackingRegionWithVerticesProducer_H 
#define RecoTracker_TkTrackingRegions_GlobalTrackingRegionWithVerticesProducer_H

#include "RecoTracker/TkTrackingRegions/interface/TrackingRegionProducer.h"
#include "RecoTracker/TkTrackingRegions/interface/GlobalTrackingRegion.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"

class GlobalTrackingRegionWithVerticesProducer : public TrackingRegionProducer
{
public:

  GlobalTrackingRegionWithVerticesProducer(const edm::ParameterSet& cfg,
	   edm::ConsumesCollector && iC)
  { 
    edm::ParameterSet regionPSet = cfg.getParameter<edm::ParameterSet>("RegionPSet");

    thePtMin            = regionPSet.getParameter<double>("ptMin");
    theOriginRadius     = regionPSet.getParameter<double>("originRadius");
    theNSigmaZ          = regionPSet.getParameter<double>("nSigmaZ");
    token_beamSpot      = iC.consumes<reco::BeamSpot>(regionPSet.getParameter<edm::InputTag>("beamSpot"));
    thePrecise          = regionPSet.getParameter<bool>("precise"); 
    theUseMS            = regionPSet.getParameter<bool>("useMultipleScattering");

    theSigmaZVertex     = regionPSet.getParameter<double>("sigmaZVertex");
    theFixedError       = regionPSet.getParameter<double>("fixedError");

    theUseFoundVertices = regionPSet.getParameter<bool>("useFoundVertices");
    theUseFakeVertices  = regionPSet.getParameter<bool>("useFakeVertices");
    theUseFixedError    = regionPSet.getParameter<bool>("useFixedError");
    token_vertex      = iC.consumes<reco::VertexCollection>(regionPSet.getParameter<edm::InputTag>("VertexCollection"));
    
    theOriginRScaling   = (regionPSet.existsAs<bool>("originRScaling4BigEvts") ? regionPSet.getParameter<bool>("originRScaling4BigEvts") : false);
    thePtMinScaling   = (regionPSet.existsAs<bool>("ptMinScaling4BigEvts") ? regionPSet.getParameter<bool>("ptMinScaling4BigEvts") : false);
    theHalfLengthScaling   = (regionPSet.existsAs<bool>("halfLengthScaling4BigEvts") ? regionPSet.getParameter<bool>("halfLengthScaling4BigEvts") : false);
    theMinOriginR       = (regionPSet.existsAs<double>("minOriginR") ? regionPSet.getParameter<double>("minOriginR") : 0.0);
    theMaxPtMin         = (regionPSet.existsAs<double>("maxPtMin") ? regionPSet.getParameter<double>("maxPtMin") : 1000.0);
    theMinHalfLength    = (regionPSet.existsAs<double>("minHalfLength") ? regionPSet.getParameter<double>("minHalfLength") : 0.0);
    theScalingStart     = (regionPSet.existsAs<double>("scalingStartNPix") ? regionPSet.getParameter<double>("scalingStartNPix") : 0.0);
    theScalingEnd       = (regionPSet.existsAs<double>("scalingEndNPix") ? regionPSet.getParameter<double>("scalingEndNPix") : 1.0);
    if(theOriginRScaling || thePtMinScaling || theHalfLengthScaling) token_pc = iC.consumes<edmNew::DetSetVector<SiPixelCluster> >(edm::InputTag("siPixelClusters"));
  }   

  virtual ~GlobalTrackingRegionWithVerticesProducer(){}

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;

    desc.add<bool>("precise", true);
    desc.add<bool>("useMultipleScattering", false);
    desc.add<edm::InputTag>("beamSpot", edm::InputTag("offlineBeamSpot"));
    desc.add<bool>("useFixedError", true);
    desc.add<double>("originRadius", 0.2);
    desc.add<double>("sigmaZVertex", 3.0);
    desc.add<double>("fixedError", 0.2);
    desc.add<edm::InputTag>("VertexCollection", edm::InputTag("firstStepPrimaryVertices"));
    desc.add<double>("ptMin", 0.9);
    desc.add<bool>("useFoundVertices", true);
    desc.add<bool>("useFakeVertices", false);
    desc.add<double>("nSigmaZ", 4.0);
    desc.add<bool>("originRScaling4BigEvts",false);
    desc.add<bool>("ptMinScaling4BigEvts",false);
    desc.add<bool>("halfLengthScaling4BigEvts",false);
    desc.add<double>("minOriginR",0);
    desc.add<double>("maxPtMin",1000);
    desc.add<double>("minHalfLength",0);
    desc.add<double>("scalingStartNPix",0.0);
    desc.add<double>("scalingEndNPix",1.0);

    // Only for backwards-compatibility
    edm::ParameterSetDescription descRegion;
    descRegion.add<edm::ParameterSetDescription>("RegionPSet", desc);

    descriptions.add("globalTrackingRegionWithVertices", descRegion);
  }

  virtual std::vector<std::unique_ptr<TrackingRegion> > regions
    (const edm::Event& ev, const edm::EventSetup&) const override
  {
    std::vector<std::unique_ptr<TrackingRegion> > result;

    GlobalPoint theOrigin;
    edm::Handle<reco::BeamSpot> bsHandle;
    ev.getByToken( token_beamSpot, bsHandle);
    double bsSigmaZ;
    if(bsHandle.isValid()) {
      const reco::BeamSpot & bs = *bsHandle; 
      bsSigmaZ = theNSigmaZ*bs.sigmaZ();
      theOrigin = GlobalPoint(bs.x0(), bs.y0(), bs.z0());
    }else{
      throw cms::Exception("Seeding") << "ERROR: input beamSpot is not valid in GlobalTrackingRegionWithVertices";
    }

    if(theUseFoundVertices)
    {
      edm::Handle<reco::VertexCollection> vertexCollection;
      ev.getByToken(token_vertex,vertexCollection);

      for(reco::VertexCollection::const_iterator iV=vertexCollection->begin(); iV != vertexCollection->end() ; iV++) {
          if (!iV->isValid()) continue;
          if (iV->isFake() && !(theUseFakeVertices && theUseFixedError)) continue;
	  GlobalPoint theOrigin_       = GlobalPoint(iV->x(),iV->y(),iV->z());

          //scaled origin radius and half length for high-occupancy HI events to keep timing reasonable
          //assumes UseFixedError is true
          if(theOriginRScaling || thePtMinScaling || theHalfLengthScaling){
            double scaledOriginRadius = theOriginRadius;
            double scaledHalfLength   = theFixedError;
            double scaledPtMin        = thePtMin;

            //calculate nPixels (adapted from TkSeedGenerator/src/ClusterChecker.cc (is there a cleaner way to doing this?)
            //does not ignore detectors above some nHit cut in order to be conservative on the nPix calculation
            double nPix = 0;
            edm::Handle<edmNew::DetSetVector<SiPixelCluster> > pixelClusterDSV;
            ev.getByToken(token_pc, pixelClusterDSV);
            if (!pixelClusterDSV.failedToGet()) {
              const edmNew::DetSetVector<SiPixelCluster> & input = *pixelClusterDSV;
              nPix = input.dataSize();
            }
            else{
              edm::LogError("GlobalTrackingRegionProducerFromBeamSpot")<<"could not get any SiPixel cluster collections of type edm::DetSetVector<SiPixelCluster>";
              nPix = theScalingEnd+1;//ensures the minimum radius is used below 
            } 

            if((nPix > theScalingEnd) || ((theScalingEnd-theScalingStart) <= 0)){//first condition is for high occupancy, second makes sure we won't divide by zero or a negative number
              if(theOriginRScaling)    scaledOriginRadius = theMinOriginR;   // sets radius to minimum value from PSet
              if(theHalfLengthScaling) scaledHalfLength = theMinHalfLength;
              if(thePtMinScaling)      scaledPtMin = theMaxPtMin; 
            }
            else if((nPix <= theScalingEnd) && (nPix > theScalingStart)){//scale radius linearly by Npix in the region from ScalingStart to ScalingEnd
              if(theOriginRScaling) scaledOriginRadius = theOriginRadius - (theOriginRadius-theMinOriginR)*(nPix-theScalingStart)/(theScalingEnd-theScalingStart);
              if(theHalfLengthScaling) scaledHalfLength = theFixedError - (theFixedError-theMinHalfLength)*(nPix-theScalingStart)/(theScalingEnd-theScalingStart);
              if(thePtMinScaling) scaledPtMin = thePtMin - (thePtMin-theMaxPtMin)*(nPix-theScalingStart)/(theScalingEnd-theScalingStart);
            }
            std::cout << "NumberOfPixels: " <<  nPix << std::endl;
            std::cout << "Scaled Origin R: " << scaledOriginRadius << " Default Origin R: " << theOriginRadius <<" Scaled HalfLength: " << scaledHalfLength << " Default H.L.: " << theFixedError <<" Scaled pT Min: " << scaledPtMin << " Default pT Min: " << thePtMin << std::endl;
            //otherwise use the unscaled radius
            if(scaledOriginRadius!=0 && scaledHalfLength !=0){
              //if region should have 0 size, return 'result' empty, otherwise make a tracking region 
              //(prevents making some tracks even with R=0 due to stat uncert on seed propagation)
              result.push_back( std::make_unique<GlobalTrackingRegion>( scaledPtMin, theOrigin_, scaledOriginRadius, scaledHalfLength, thePrecise,theUseMS));
            }
          }//end of linear scaling code
          else{
	    double theOriginHalfLength_ = (theUseFixedError ? theFixedError : (iV->zError())*theSigmaZVertex); 
	    result.push_back( std::make_unique<GlobalTrackingRegion>(thePtMin, theOrigin_, theOriginRadius, theOriginHalfLength_, thePrecise, theUseMS) );
          }
      }
      
      if (result.empty() && !(theOriginRScaling || thePtMinScaling || theHalfLengthScaling)) {
        result.push_back( std::make_unique<GlobalTrackingRegion>(thePtMin, theOrigin, theOriginRadius, bsSigmaZ, thePrecise, theUseMS) );
      }
    }
    else
    {
      result.push_back(
        std::make_unique<GlobalTrackingRegion>(thePtMin, theOrigin, theOriginRadius, bsSigmaZ, thePrecise, theUseMS) );
    }

    return result;
  }

private:
  double thePtMin; 
  double theOriginRadius; 
  double theNSigmaZ;
  edm::InputTag theBeamSpotTag;

  double theSigmaZVertex;
  double theFixedError;
  bool thePrecise;
  bool theUseMS;
  
  bool theUseFoundVertices;
  bool theUseFakeVertices;
  bool theUseFixedError;
  edm::EDGetTokenT<reco::VertexCollection> 	 token_vertex; 
  edm::EDGetTokenT<reco::BeamSpot> 	 token_beamSpot; 

  bool theOriginRScaling; 
  bool thePtMinScaling; 
  bool theHalfLengthScaling; 
  double theMinOriginR;
  double theMaxPtMin;
  double theMinHalfLength;
  double theScalingStart;   
  double theScalingEnd;
  edm::EDGetTokenT<edmNew::DetSetVector<SiPixelCluster> > token_pc;
};

#endif 
