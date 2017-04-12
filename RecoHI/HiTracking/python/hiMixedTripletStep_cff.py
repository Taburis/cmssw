import FWCore.ParameterSet.Config as cms
from RecoTracker.IterativeTracking.MixedTripletStep_cff import *
from HIPixelTripletSeeds_cff import *
from HIPixel3PrimTracks_cfi import *


###############################################################
# Large impact parameter Tracking using mixed-triplet seeding #
###############################################################


#here just for backward compatibility
# chargeCut2069Clusters =  cms.EDProducer("ClusterChargeMasker",
#     oldClusterRemovalInfo = cms.InputTag(""), # to be set below
#     pixelClusters = cms.InputTag("siPixelClusters"),
#     stripClusters = cms.InputTag("siStripClusters"),
#     clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight'))
# )

#cluster remover
hiMixedTripletStepClusters = cms.EDProducer("HITrackClusterRemover",
     clusterLessSolution = cms.bool(True),
     trajectories = cms.InputTag("hiPixelPairGlobalPrimTracks"),
     overrideTrkQuals = cms.InputTag('hiPixelPairStepSelector','hiPixelPairStep'),
     TrackQuality = cms.string('highPurity'),
     minNumberOfLayersWithMeasBeforeFiltering = cms.int32(0),
     pixelClusters = cms.InputTag("siPixelClusters"),
     stripClusters = cms.InputTag("siStripClusters"),
     Common = cms.PSet(
         maxChi2 = cms.double(9.0),
     ),
     Strip = cms.PSet(
        #Yen-Jie's mod to preserve merged clusters
        maxSize = cms.uint32(2),
        maxChi2 = cms.double(9.0)
     )
)

# SEEDING LAYERS
from RecoLocalTracker.SiStripClusterizer.SiStripClusterChargeCut_cfi import *
from RecoTracker.IterativeTracking.DetachedTripletStep_cff import detachedTripletStepSeedLayers
hiMixedTripletStepSeedLayersA = cms.EDProducer("SeedingLayersEDProducer",
     layerList = cms.vstring('BPix2+FPix1_pos+FPix2_pos', 'BPix2+FPix1_neg+FPix2_neg'),
#    layerList = cms.vstring('BPix1+BPix2+BPix3', 
#        'BPix1+BPix2+FPix1_pos', 'BPix1+BPix2+FPix1_neg', 
#        'BPix1+FPix1_pos+FPix2_pos', 'BPix1+FPix1_neg+FPix2_neg', 
#        'BPix2+FPix1_pos+FPix2_pos', 'BPix2+FPix1_neg+FPix2_neg'),
    BPix = cms.PSet(
        TTRHBuilder = cms.string('WithTrackAngle'),
        HitProducer = cms.string('siPixelRecHits'),
        skipClusters = cms.InputTag('hiMixedTripletStepClusters')
    ),
    FPix = cms.PSet(
        TTRHBuilder = cms.string('WithTrackAngle'),
        HitProducer = cms.string('siPixelRecHits'),
        skipClusters = cms.InputTag('hiMixedTripletStepClusters')
    ),
    TEC = cms.PSet(
        matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
        useRingSlector = cms.bool(True),
        TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
        minRing = cms.int32(1),
        maxRing = cms.int32(1),
        skipClusters = cms.InputTag('hiMixedTripletStepClusters')
    )
)


# TrackingRegion
# from RecoTracker.TkTrackingRegions.globalTrackingRegionFromBeamSpotFixedZ_cfi import globalTrackingRegionFromBeamSpotFixedZ as _globalTrackingRegionFromBeamSpotFixedZ
# mixedTripletStepTrackingRegionsA = _globalTrackingRegionFromBeamSpotFixedZ.clone(RegionPSet = dict(
#     ptMin = 0.4,
#     originHalfLength = 15.0,
#     originRadius = 1.5
# ))

from RecoTracker.TkTrackingRegions.globalTrackingRegionWithVertices_cfi import globalTrackingRegionWithVertices as _globalTrackingRegionWithVertices
from RecoTracker.TkHitPairs.hitPairEDProducer_cfi import hitPairEDProducer as _hitPairEDProducer
from RecoPixelVertexing.PixelTriplets.pixelTripletHLTEDProducer_cfi import pixelTripletHLTEDProducer as _pixelTripletHLTEDProducer
from RecoPixelVertexing.PixelLowPtUtilities.ClusterShapeHitFilterESProducer_cfi import *
from RecoPixelVertexing.PixelLowPtUtilities.trackCleaner_cfi import *
from RecoPixelVertexing.PixelTrackFitting.pixelFitterByHelixProjections_cfi import *
from RecoHI.HiTracking.HIPixelTrackFilter_cff import *
from RecoHI.HiTracking.HITrackingRegionProducer_cfi import *

hiMixedTripletStepTrackingRegionsA = _globalTrackingRegionWithVertices.clone(RegionPSet=dict(
    precise = True,
    useMultipleScattering = False,
    useFakeVertices       = False,
    beamSpot = "offlineBeamSpot",
    useFixedError = True,
    nSigmaZ = 4.0,
    sigmaZVertex = 4.0,
    fixedError = 0.5,
    VertexCollection = "hiSelectedVertex",
    ptMin = 0.8,#0.4
    useFoundVertices = True,
    #originHalfLength = 15.0,
    originRadius = 1.5#1.5
))

# seeding
from RecoPixelVertexing.PixelLowPtUtilities.ClusterShapeHitFilterESProducer_cfi import ClusterShapeHitFilterESProducer as _ClusterShapeHitFilterESProducer
hiMixedTripletStepClusterShapeHitFilter  = _ClusterShapeHitFilterESProducer.clone(
    ComponentName = 'hiMixedTripletStepClusterShapeHitFilter',
    clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutTight')
)
from RecoTracker.TkHitPairs.hitPairEDProducer_cfi import hitPairEDProducer as _hitPairEDProducer
hiMixedTripletStepHitDoubletsA = _hitPairEDProducer.clone(
    clusterCheck = "",
    seedingLayers = "hiMixedTripletStepSeedLayersA",
    trackingRegions = "hiMixedTripletStepTrackingRegionsA",
    maxElement = 0,
    produceIntermediateHitDoublets = True,
)
from RecoPixelVertexing.PixelTriplets.pixelTripletLargeTipEDProducer_cfi import pixelTripletLargeTipEDProducer as _pixelTripletLargeTipEDProducer
from RecoPixelVertexing.PixelLowPtUtilities.ClusterShapeHitFilterESProducer_cfi import *
hiMixedTripletStepHitTripletsA = _pixelTripletLargeTipEDProducer.clone(
    doublets = "hiMixedTripletStepHitDoubletsA",
    produceSeedingHitSets = True,
)

from RecoTracker.TkSeedGenerator.seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer_cff import seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer as _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer
hiMixedTripletStepSeedsA = _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer.clone(
    seedingHitSets = "hiMixedTripletStepHitTripletsA",
    SeedComparitorPSet = dict(# FIXME: is this defined in any cfi that could be imported instead of copy-paste?
        ComponentName = 'PixelClusterShapeSeedComparitor',
        FilterAtHelixStage = cms.bool(False),
        FilterPixelHits = cms.bool(True),
        FilterStripHits = cms.bool(True),
        ClusterShapeHitFilterName = cms.string('hiMixedTripletStepClusterShapeHitFilter'),
        ClusterShapeCacheSrc = cms.InputTag('siPixelClusterShapeCache')
    ),
)


# SEEDING LAYERS
hiMixedTripletStepSeedLayersB = cms.EDProducer("SeedingLayersEDProducer",
    layerList = cms.vstring('BPix2+BPix3+TIB1'),
    BPix = cms.PSet(
        TTRHBuilder = cms.string('WithTrackAngle'),
        HitProducer = cms.string('siPixelRecHits'),
        skipClusters = cms.InputTag('hiMixedTripletStepClusters')
    ),
    TIB = cms.PSet(
        matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
        TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
        skipClusters = cms.InputTag('hiMixedTripletStepClusters')
    )
)

# TrackingRegion
hiMixedTripletStepTrackingRegionsB = _globalTrackingRegionWithVertices.clone(RegionPSet=dict(
    precise = True,
    useMultipleScattering = False,
    useFakeVertices       = False,
    beamSpot = "offlineBeamSpot",
    useFixedError = True,
    nSigmaZ = 4.0,
    sigmaZVertex = 4.0,
    fixedError = 0.5,
    VertexCollection = "hiSelectedVertex",
    ptMin = 0.8,#0.4
    useFoundVertices = True,
    #originHalfLength = 15.0,
    originRadius = 1.5#1.5
))


# seeding
hiMixedTripletStepHitDoubletsB = hiMixedTripletStepHitDoubletsA.clone(
    seedingLayers = "hiMixedTripletStepSeedLayersB",
    trackingRegions = "hiMixedTripletStepTrackingRegionsB",
)
hiMixedTripletStepHitTripletsB = hiMixedTripletStepHitTripletsA.clone(doublets = "hiMixedTripletStepHitDoubletsB")
hiMixedTripletStepSeedsB = hiMixedTripletStepSeedsA.clone(seedingHitSets = "hiMixedTripletStepHitTripletsB")

import RecoTracker.TkSeedGenerator.GlobalCombinedSeeds_cfi
hiMixedTripletStepSeeds = RecoTracker.TkSeedGenerator.GlobalCombinedSeeds_cfi.globalCombinedSeeds.clone()
hiMixedTripletStepSeeds.seedCollections = cms.VInputTag(
        cms.InputTag('hiMixedTripletStepSeedsA'),
        cms.InputTag('hiMixedTripletStepSeedsB'),
        )

# QUALITY CUTS DURING TRACK BUILDING
import TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff
_hiMixedTripletStepTrajectoryFilterBase = TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff.CkfBaseTrajectoryFilter_block.clone(
#    maxLostHits = 0,
    minimumNumberOfHits = 3,
    minPt = 0.1
)
hiMixedTripletStepTrajectoryFilter = _hiMixedTripletStepTrajectoryFilterBase.clone(
    constantValueForLostHitsFractionFilter = 1.4,
)

# Propagator taking into account momentum uncertainty in multiple scattering calculation.
import TrackingTools.MaterialEffects.MaterialPropagatorParabolicMf_cff
import TrackingTools.MaterialEffects.MaterialPropagator_cfi
hiMixedTripletStepPropagator = TrackingTools.MaterialEffects.MaterialPropagator_cfi.MaterialPropagator.clone(
#hiMixedTripletStepPropagator = TrackingTools.MaterialEffects.MaterialPropagatorParabolicMf_cff.MaterialPropagatorParabolicMF.clone(
    ComponentName = 'hiMixedTripletStepPropagator',
    ptMin = 0.1
    )

import TrackingTools.MaterialEffects.OppositeMaterialPropagator_cfi
hiMixedTripletStepPropagatorOpposite = TrackingTools.MaterialEffects.OppositeMaterialPropagator_cfi.OppositeMaterialPropagator.clone(
#hiMixedTripletStepPropagatorOpposite = TrackingTools.MaterialEffects.MaterialPropagatorParabolicMf_cff.OppositeMaterialPropagatorParabolicMF.clone(
    ComponentName = 'hiMixedTripletStepPropagatorOpposite',
    ptMin = 0.1
    )

import RecoTracker.MeasurementDet.Chi2ChargeMeasurementEstimator_cfi
hiMixedTripletStepChi2Est = RecoTracker.MeasurementDet.Chi2ChargeMeasurementEstimator_cfi.Chi2ChargeMeasurementEstimator.clone(
    ComponentName = cms.string('hiMixedTripletStepChi2Est'),
    nSigma = cms.double(3.0),
    MaxChi2 = cms.double(16.0),
    clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight'))
)


# TRACK BUILDING
import RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi
hiMixedTripletStepTrajectoryBuilder = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi.GroupedCkfTrajectoryBuilder.clone(
    MeasurementTrackerName = '',
    trajectoryFilter = cms.PSet(refToPSet_ = cms.string('hiMixedTripletStepTrajectoryFilter')),
    propagatorAlong = cms.string('hiMixedTripletStepPropagator'),
    propagatorOpposite = cms.string('hiMixedTripletStepPropagatorOpposite'),
    maxCand = 2,
    estimator = cms.string('hiMixedTripletStepChi2Est'),
    maxDPhiForLooperReconstruction = cms.double(2.0),
    maxPtForLooperReconstruction = cms.double(0.7) 
    )

# MAKING OF TRACK CANDIDATES
import RecoTracker.CkfPattern.CkfTrackCandidates_cfi
hiMixedTripletStepTrackCandidates = RecoTracker.CkfPattern.CkfTrackCandidates_cfi.ckfTrackCandidates.clone(
    src = cms.InputTag('hiMixedTripletStepSeeds'),
    clustersToSkip = cms.InputTag('hiMixedTripletStepClusters'),
    ### these two parameters are relevant only for the CachingSeedCleanerBySharedInput
    numHitsForSeedCleaner = cms.int32(50),
    #onlyPixelHitsForSeedCleaner = cms.bool(True),

    TrajectoryBuilderPSet = cms.PSet(refToPSet_ = cms.string('hiMixedTripletStepTrajectoryBuilder')),
    doSeedingRegionRebuilding = True,
    useHitsSplitting = True
)


from TrackingTools.TrajectoryCleaning.TrajectoryCleanerBySharedHits_cfi import trajectoryCleanerBySharedHits
hiMixedTripletStepTrajectoryCleanerBySharedHits = trajectoryCleanerBySharedHits.clone(
        ComponentName = cms.string('hiMixedTripletStepTrajectoryCleanerBySharedHits'),
            fractionShared = cms.double(0.11),
            allowSharedFirstHit = cms.bool(True)
            )
hiMixedTripletStepTrackCandidates.TrajectoryCleaner = 'hiMixedTripletStepTrajectoryCleanerBySharedHits'


# TRACK FITTING
import RecoTracker.TrackProducer.TrackProducer_cfi
hiMixedTripletStepTracks = RecoTracker.TrackProducer.TrackProducer_cfi.TrackProducer.clone(
    AlgorithmName = cms.string('hiMixedTripletStep'),
    src = 'hiMixedTripletStepTrackCandidates',
    Fitter = cms.string('FlexibleKFFittingSmoother')
)

# Final selection
import RecoHI.HiTracking.hiMultiTrackSelector_cfi
hiMixedTripletStepSelector = RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiMultiTrackSelector.clone(
    src='hiMixedTripletStepTracks',
    useAnyMVA = cms.bool(True),
    GBRForestLabel = cms.string('HIMVASelectorIter11'),
    GBRForestVars = cms.vstring(['chi2perdofperlayer', 'nhits', 'nlayers', 'eta']),
    trackSelectors= cms.VPSet(
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiLooseMTS.clone(
    name = 'hiMixedTripletStepLoose',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    ), #end of pset
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiTightMTS.clone(
    name = 'hiMixedTripletStepTight',
    preFilterName = 'hiMixedTripletStepLoose',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    minMVA = cms.double(-0.2)
    ),
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiHighpurityMTS.clone(
    name = 'hiMixedTripletStep',
    preFilterName = 'hiMixedTripletStepTight',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    minMVA = cms.double(-0.09)
    ),
    ) #end of vpset
    ) #end of clone

import RecoTracker.FinalTrackSelectors.trackListMerger_cfi
hiMixedTripletStepQual = RecoTracker.FinalTrackSelectors.trackListMerger_cfi.trackListMerger.clone(
    TrackProducers=cms.VInputTag(cms.InputTag('hiMixedTripletStepTracks')),
    hasSelector=cms.vint32(1),
    selectedTrackQuals = cms.VInputTag(cms.InputTag("hiMixedTripletStepSelector","hiMixedTripletStep")),
    copyExtras = True,
    makeReKeyedSeeds = cms.untracked.bool(False),
    )


# import RecoTracker.FinalTrackSelectors.trackListMerger_cfi
# _trackListMergerBase = RecoTracker.FinalTrackSelectors.trackListMerger_cfi.trackListMerger.clone(
#     TrackProducers = ['mixedTripletStepTracks',
#                       'mixedTripletStepTracks'],
#     hasSelector = [1,1],
#     selectedTrackQuals = [cms.InputTag("mixedTripletStepSelector","mixedTripletStepVtx"),
#                           cms.InputTag("mixedTripletStepSelector","mixedTripletStepTrk")],
#     setsToMerge = [cms.PSet( tLists=cms.vint32(0,1), pQual=cms.bool(True) )],
#     writeOnlyTrkQuals = True
# )




hiMixedTripletStep = cms.Sequence(#chargeCut2069Clusters*
                                hiMixedTripletStepClusters*
                                hiMixedTripletStepSeedLayersA*
                                hiMixedTripletStepTrackingRegionsA*
                                hiMixedTripletStepHitDoubletsA*
                                hiMixedTripletStepHitTripletsA*
                                hiMixedTripletStepSeedsA*
                                hiMixedTripletStepSeedLayersB*
                                hiMixedTripletStepTrackingRegionsB*
                                hiMixedTripletStepHitDoubletsB*
                                hiMixedTripletStepHitTripletsB*
                                hiMixedTripletStepSeedsB*
                                hiMixedTripletStepSeeds*
                                hiMixedTripletStepTrackCandidates*
                                hiMixedTripletStepTracks*
                                hiMixedTripletStepSelector*
                                hiMixedTripletStepQual)
