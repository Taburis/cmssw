from RecoHI.HiTracking.hiMergedConformalPixelTracking_cff import *
from RecoHI.HiTracking.HIInitialJetCoreClusterSplitting_cff import *
from RecoHI.HiTracking.HighPtTracking_PbPb_cff import *
from RecoHI.HiTracking.hiLowPtTripletStep_cff import *
from RecoHI.HiTracking.hiMixedTripletStep_cff import *
from RecoHI.HiTracking.hiPixelPairStep_cff import *
from RecoHI.HiTracking.hiDetachedTripletStep_cff import *
from RecoHI.HiTracking.hiJetCoreRegionalStep_cff import *
from RecoHI.HiTracking.MergeTrackCollectionsHI_cff import *
from RecoHI.HiTracking.hiLowPtQuadStep_cff import *
from RecoHI.HiTracking.hiHighPtTripletStep_cff import *
from RecoHI.HiTracking.hiDetachedQuadStep_cff import *
from RecoHI.HiTracking.hiMixedTripletStep_cff import *
from RecoHI.HiTracking.hiPixelLessStep_cff import *
from RecoHI.HiTracking.hiTobTecStep_cff import *

from RecoHI.HiMuonAlgos.hiMuonIterativeTk_cff import *

hiJetsForCoreTracking.cut = cms.string("pt > 100 && abs(eta) < 2.4")
hiJetCoreRegionalStepSeeds.RegionFactoryPSet.RegionPSet.ptMin = cms.double( 10. )
hiJetCoreRegionalStepTrajectoryFilter.minPt = 10.0
siPixelClusters.ptMin = cms.double(100)
siPixelClusters.deltaRmax = cms.double(0.1)

hiTracking_noRegitMu = cms.Sequence(
    hiBasicTracking
    *hiDetachedTripletStep
    *hiLowPtTripletStep
    *hiPixelPairStep
    )

hiTracking_noRegitMu_wSplitting = cms.Sequence(
    hiInitialJetCoreClusterSplitting
    *hiBasicTracking
    *hiDetachedTripletStep
    *hiLowPtTripletStep
    *hiPixelPairStep
    )

hiTracking_noRegitMu_wSplitting_Phase1 = cms.Sequence(
    hiInitialJetCoreClusterSplitting
    *hiBasicTracking
    *hiLowPtQuadStep#New iteration
    *hiHighPtTripletStep#New iteration
    *hiDetachedQuadStep#New iteration
    *hiDetachedTripletStep
    *hiLowPtTripletStep
    *hiPixelPairStep #no CA seeding implemented
    *hiMixedTripletStep #New iteration large impact parameter tracks
    *hiPixelLessStep #New iteration large impact parameter tracks
    *hiTobTecStep
    )

hiTracking = cms.Sequence(
    hiTracking_noRegitMu
    *hiRegitMuTrackingAndSta
    *hiGeneralTracks
    )

hiTracking_wSplitting = cms.Sequence(
    hiTracking_noRegitMu_wSplitting
    *hiJetCoreRegionalStep 
    *hiRegitMuTrackingAndSta
    *hiGeneralTracks
    )

hiTracking_wSplitting_Phase1 = cms.Sequence(
    hiTracking_noRegitMu_wSplitting_Phase1
    *hiJetCoreRegionalStep 
    *hiRegitMuTrackingAndSta
    *hiGeneralTracks
    *bestFinalHiVertex
    )

hiTracking_wConformalPixel = cms.Sequence(
    hiTracking
    *hiMergedConformalPixelTracking 
    )
