import FWCore.ParameterSet.Config as cms
import RecoTracker.IterativeTracking.iterativeTkConfig as _cfg
from RecoTracker.IterativeTracking.TobTecStep_cff import *
from HIPixelTripletSeeds_cff import *
from HIPixel3PrimTracks_cfi import *

#######################################################################
# Very large impact parameter tracking using TOB + TEC ring 5 seeding #
#######################################################################
hiTobTecStepClusters = cms.EDProducer("HITrackClusterRemover",
     clusterLessSolution = cms.bool(True),
     trajectories = cms.InputTag("hiPixelLessStepTracks"),
     overrideTrkQuals = cms.InputTag('hiPixelLessStepSelector','hiPixelLessStep'),
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

# TRIPLET SEEDING LAYERS
from RecoLocalTracker.SiStripClusterizer.SiStripClusterChargeCut_cfi import *
hiTobTecStepSeedLayersTripl = cms.EDProducer("SeedingLayersEDProducer",
    layerList = cms.vstring(
    #TOB
    'TOB1+TOB2+MTOB3','TOB1+TOB2+MTOB4',
    #TOB+MTEC
    'TOB1+TOB2+MTEC1_pos','TOB1+TOB2+MTEC1_neg',
    ),
    TOB = cms.PSet(
         TTRHBuilder    = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
         matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
         skipClusters   = cms.InputTag('hiTobTecStepClusters')
    ),
    MTOB = cms.PSet(
         TTRHBuilder    = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
         skipClusters   = cms.InputTag('hiTobTecStepClusters'),
         rphiRecHits    = cms.InputTag("siStripMatchedRecHits","rphiRecHit")
    ),
    MTEC = cms.PSet(
        rphiRecHits    = cms.InputTag("siStripMatchedRecHits","rphiRecHit"),
        skipClusters = cms.InputTag('hiTobTecStepClusters'),
        useRingSlector = cms.bool(True),
        TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
        minRing = cms.int32(6),
        maxRing = cms.int32(7)
    )
)

# Triplet TrackingRegion
from RecoTracker.TkTrackingRegions.globalTrackingRegionFromBeamSpotFixedZ_cfi import globalTrackingRegionFromBeamSpotFixedZ as _globalTrackingRegionFromBeamSpotFixedZ
hiTobTecStepTrackingRegionsTripl = _globalTrackingRegionFromBeamSpotFixedZ.clone(RegionPSet = dict(
    ptMin = 0.55,
    originHalfLength = 20.0,
    originRadius = 3.5,
    originRScaling4BigEvts = cms.bool(True),
    halfLengthScaling4BigEvts = cms.bool(True),
    ptMinScaling4BigEvts = cms.bool(True),
    minOriginR = 0,
    minHalfLength = 20,
    maxPtMin = 5,
    scalingStartNPix = 20000,
    scalingEndNPix = 35000
))

# Triplet seeding
from RecoPixelVertexing.PixelLowPtUtilities.ClusterShapeHitFilterESProducer_cfi import ClusterShapeHitFilterESProducer as _ClusterShapeHitFilterESProducer
hiTobTecStepClusterShapeHitFilter = _ClusterShapeHitFilterESProducer.clone(
    ComponentName = 'hiTobTecStepClusterShapeHitFilter',
    doStripShapeCut = cms.bool(False),
    clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutTight')
)

from RecoTracker.TkHitPairs.hitPairEDProducer_cfi import hitPairEDProducer as _hitPairEDProducer
hiTobTecStepHitDoubletsTripl = _hitPairEDProducer.clone(
    clusterCheck = "",
    seedingLayers = "hiTobTecStepSeedLayersTripl",
    trackingRegions = "hiTobTecStepTrackingRegionsTripl",
    maxElement = 0,
    produceIntermediateHitDoublets = True,
)
from RecoTracker.TkSeedGenerator.multiHitFromChi2EDProducer_cfi import multiHitFromChi2EDProducer as _multiHitFromChi2EDProducer
hiTobTecStepHitTripletsTripl = _multiHitFromChi2EDProducer.clone(
    doublets = "hiTobTecStepHitDoubletsTripl",
    extraPhiKDBox = 0.01,
)
from RecoTracker.TkSeedGenerator.seedCreatorFromRegionConsecutiveHitsEDProducer_cff import seedCreatorFromRegionConsecutiveHitsEDProducer as _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer
from RecoPixelVertexing.PixelLowPtUtilities.StripSubClusterShapeSeedFilter_cfi import StripSubClusterShapeSeedFilter as _StripSubClusterShapeSeedFilter
_hiTobTecStepSeedComparitorPSet = dict(
    ComponentName = 'CombinedSeedComparitor',
    mode = cms.string("and"),
    comparitors = cms.VPSet(
        cms.PSet(# FIXME: is this defined in any cfi that could be imported instead of copy-paste?
            ComponentName = cms.string('PixelClusterShapeSeedComparitor'),
            FilterAtHelixStage = cms.bool(True),
            FilterPixelHits = cms.bool(False),
            FilterStripHits = cms.bool(True),
            ClusterShapeHitFilterName = cms.string('hiTobTecStepClusterShapeHitFilter'),
            ClusterShapeCacheSrc = cms.InputTag("siPixelClusterShapeCache") # not really needed here since FilterPixelHits=False
        ),
        _StripSubClusterShapeSeedFilter.clone()
    )
)
hiTobTecStepSeedsTripl = _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer.clone(#empirically better than 'SeedFromConsecutiveHitsTripletOnlyCreator'
    seedingHitSets = "hiTobTecStepHitTripletsTripl",
    SeedComparitorPSet = _hiTobTecStepSeedComparitorPSet,
)


# PAIR SEEDING LAYERS
hiTobTecStepSeedLayersPair = cms.EDProducer("SeedingLayersEDProducer",
    layerList = cms.vstring('TOB1+TEC1_pos','TOB1+TEC1_neg', 
                            'TEC1_pos+TEC2_pos','TEC1_neg+TEC2_neg', 
                            'TEC2_pos+TEC3_pos','TEC2_neg+TEC3_neg', 
                            'TEC3_pos+TEC4_pos','TEC3_neg+TEC4_neg', 
                            'TEC4_pos+TEC5_pos','TEC4_neg+TEC5_neg', 
                            'TEC5_pos+TEC6_pos','TEC5_neg+TEC6_neg', 
                            'TEC6_pos+TEC7_pos','TEC6_neg+TEC7_neg'),
    TOB = cms.PSet(
         TTRHBuilder    = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
         matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
         skipClusters   = cms.InputTag('hiTobTecStepClusters')
    ),
    TEC = cms.PSet(
        matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
        skipClusters = cms.InputTag('hiTobTecStepClusters'),
        useRingSlector = cms.bool(True),
        TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight')),
        minRing = cms.int32(5),
        maxRing = cms.int32(5)
    )
)
# Pair TrackingRegion
hiTobTecStepTrackingRegionsPair = _globalTrackingRegionFromBeamSpotFixedZ.clone(RegionPSet = dict(
    ptMin = 0.6,
    originHalfLength = 30.0,
    originRadius = 6.0,
    originRScaling4BigEvts = cms.bool(True),
    halfLengthScaling4BigEvts = cms.bool(True),
    ptMinScaling4BigEvts = cms.bool(True),
    minOriginR = 0,
    minHalfLength = 20,
    maxPtMin = 5,
    scalingStartNPix = 20000,
    scalingEndNPix = 35000
))

# Pair seeds
hiTobTecStepHitDoubletsPair = _hitPairEDProducer.clone(
    clusterCheck = "",
    seedingLayers = "hiTobTecStepSeedLayersPair",
    trackingRegions = "hiTobTecStepTrackingRegionsPair",
    produceSeedingHitSets = True,
)
from RecoTracker.TkSeedGenerator.seedCreatorFromRegionConsecutiveHitsEDProducer_cff import seedCreatorFromRegionConsecutiveHitsEDProducer as _seedCreatorFromRegionConsecutiveHitsEDProducer
hiTobTecStepSeedsPair = _seedCreatorFromRegionConsecutiveHitsEDProducer.clone(
    seedingHitSets = "hiTobTecStepHitDoubletsPair",
    SeedComparitorPSet = _hiTobTecStepSeedComparitorPSet,
)

# Combined seeds
import RecoTracker.TkSeedGenerator.GlobalCombinedSeeds_cfi
hiTobTecStepSeeds = RecoTracker.TkSeedGenerator.GlobalCombinedSeeds_cfi.globalCombinedSeeds.clone()
hiTobTecStepSeeds.seedCollections = cms.VInputTag(cms.InputTag('hiTobTecStepSeedsTripl'),cms.InputTag('hiTobTecStepSeedsPair'))

# LowPU
from Configuration.Eras.Modifier_trackingLowPU_cff import trackingLowPU
trackingLowPU.toModify(hiTobTecStepHitDoubletsPair, seedingLayers = 'hiTobTecStepSeedLayers')
trackingLowPU.toReplaceWith(hiTobTecStepSeeds, _seedCreatorFromRegionConsecutiveHitsEDProducer.clone(
    seedingHitSets = "hiTobTecStepHitDoubletsPair",
))
# Phase1PU70
from Configuration.Eras.Modifier_trackingPhase1PU70_cff import trackingPhase1PU70
trackingPhase1PU70.toModify(hiTobTecStepTrackingRegionsPair, RegionPSet = dict(
    ptMin = 1.0,
    originHalfLength = 15.0,
    originRadius = 2.0
))
trackingPhase1PU70.toModify(hiTobTecStepHitDoubletsPair, seedingLayers = 'hiTobTecStepSeedLayers')
trackingPhase1PU70.toReplaceWith(hiTobTecStepSeeds, hiTobTecStepSeedsPair.clone(
    OriginTransverseErrorMultiplier = 3.0,
    SeedComparitorPSet = cms.PSet(# FIXME: is this defined in any cfi that could be imported instead of copy-paste?
        ComponentName = cms.string('PixelClusterShapeSeedComparitor'),
        FilterAtHelixStage = cms.bool(True),
        FilterPixelHits = cms.bool(False),
        FilterStripHits = cms.bool(True),
        ClusterShapeHitFilterName = cms.string('ClusterShapeHitFilter'),
        ClusterShapeCacheSrc = cms.InputTag("siPixelClusterShapeCache") # not really needed here since FilterPixelHits=False
    ),
))


# QUALITY CUTS DURING TRACK BUILDING (for inwardss and outwards track building steps)
import TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff
_hiTobTecStepTrajectoryFilterBase = TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff.CkfBaseTrajectoryFilter_block.clone(
    maxLostHits = 0,
    minimumNumberOfHits = 5,
    minPt = 0.1,
    minHitsMinPt = 3
    )
hiTobTecStepTrajectoryFilter = _hiTobTecStepTrajectoryFilterBase.clone(
    seedPairPenalty = 1,
)
trackingLowPU.toReplaceWith(hiTobTecStepTrajectoryFilter, _hiTobTecStepTrajectoryFilterBase.clone(
    minimumNumberOfHits = 6,
))
trackingPhase1PU70.toReplaceWith(hiTobTecStepTrajectoryFilter, _hiTobTecStepTrajectoryFilterBase.clone(
    minimumNumberOfHits = 6,
))

hiTobTecStepInOutTrajectoryFilter = hiTobTecStepTrajectoryFilter.clone(
    minimumNumberOfHits = 4,
)


import RecoTracker.MeasurementDet.Chi2ChargeMeasurementEstimator_cfi
hiTobTecStepChi2Est = RecoTracker.MeasurementDet.Chi2ChargeMeasurementEstimator_cfi.Chi2ChargeMeasurementEstimator.clone(
    ComponentName = cms.string('hiTobTecStepChi2Est'),
    nSigma = cms.double(3.0),
    MaxChi2 = cms.double(16.0),
    clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTight'))
)
trackingLowPU.toModify(hiTobTecStepChi2Est,
    clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutTiny')
)
trackingPhase1PU70.toModify(hiTobTecStepChi2Est,
    MaxChi2 = 9.0,
    clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutNone'),
)

# TRACK BUILDING
import RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi
hiTobTecStepTrajectoryBuilder = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi.GroupedCkfTrajectoryBuilder.clone(
    MeasurementTrackerName = '',
    trajectoryFilter = cms.PSet(refToPSet_ = cms.string('hiTobTecStepTrajectoryFilter')),
    inOutTrajectoryFilter = cms.PSet(refToPSet_ = cms.string('hiTobTecStepInOutTrajectoryFilter')),
    useSameTrajFilter = False,
    minNrOfHitsForRebuild = 4,
    alwaysUseInvalidHits = False,
    maxCand = 2,
    estimator = cms.string('hiTobTecStepChi2Est'),
    #startSeedHitsInRebuild = True
    maxDPhiForLooperReconstruction = cms.double(2.0),
    maxPtForLooperReconstruction = cms.double(0.7)
    )
# Important note for LowPU: in RunI_TobTecStep the
# inOutTrajectoryFilter parameter is spelled as
# inOutTrajectoryFilterName, and I suspect it has no effect there. I
# chose to "fix" the behaviour here, so the era is not fully
# equivalent to the customize. To restore the customize behaviour,
# uncomment the following lines
#trackingLowPU.toModify(tobTecStepTrajectoryBuilder,
#    inOutTrajectoryFilter = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi.GroupedCkfTrajectoryBuilder.inOutTrajectoryFilter.clone(),
#    inOutTrajectoryFilterName = cms.PSet(refToPSet_ = cms.string('tobTecStepInOutTrajectoryFilter'))
#)

# MAKING OF TRACK CANDIDATES
import RecoTracker.CkfPattern.CkfTrackCandidates_cfi
hiTobTecStepTrackCandidates = RecoTracker.CkfPattern.CkfTrackCandidates_cfi.ckfTrackCandidates.clone(
    src = cms.InputTag('hiTobTecStepSeeds'),
    clustersToSkip = cms.InputTag('hiTobTecStepClusters'),
    ### these two parameters are relevant only for the CachingSeedCleanerBySharedInput
    numHitsForSeedCleaner = cms.int32(50),
    onlyPixelHitsForSeedCleaner = cms.bool(True),

    TrajectoryBuilderPSet = cms.PSet(refToPSet_ = cms.string('hiTobTecStepTrajectoryBuilder')),
    doSeedingRegionRebuilding = True,
    useHitsSplitting = True,
    cleanTrajectoryAfterInOut = True
)

from TrackingTools.TrajectoryCleaning.TrajectoryCleanerBySharedHits_cfi import trajectoryCleanerBySharedHits
hiTobTecStepTrajectoryCleanerBySharedHits = trajectoryCleanerBySharedHits.clone(
    ComponentName = cms.string('hiTobTecStepTrajectoryCleanerBySharedHits'),
    fractionShared = cms.double(0.09),
    allowSharedFirstHit = cms.bool(True)
    )
hiTobTecStepTrackCandidates.TrajectoryCleaner = 'hiTobTecStepTrajectoryCleanerBySharedHits'
trackingLowPU.toModify(hiTobTecStepTrajectoryCleanerBySharedHits, fractionShared = 0.19)
trackingPhase1PU70.toModify(hiTobTecStepTrajectoryCleanerBySharedHits, fractionShared = 0.08)

# TRACK FITTING AND SMOOTHING OPTIONS
import TrackingTools.TrackFitters.RungeKuttaFitters_cff
hiTobTecStepFitterSmoother = TrackingTools.TrackFitters.RungeKuttaFitters_cff.KFFittingSmootherWithOutliersRejectionAndRK.clone(
    ComponentName = 'hiTobTecStepFitterSmoother',
    EstimateCut = 30,
    MinNumberOfHits = 7,
    Fitter = cms.string('hiTobTecStepRKFitter'),
    Smoother = cms.string('hiTobTecStepRKSmoother')
    )
trackingLowPU.toModify(hiTobTecStepFitterSmoother, MinNumberOfHits = 8)
trackingPhase1PU70.toModify(hiTobTecStepFitterSmoother, MinNumberOfHits = 8)

hiTobTecStepFitterSmootherForLoopers = hiTobTecStepFitterSmoother.clone(
    ComponentName = 'hiTobTecStepFitterSmootherForLoopers',
    Fitter = cms.string('hiTobTecStepRKFitterForLoopers'),
    Smoother = cms.string('hiTobTecStepRKSmootherForLoopers')
)

# Also necessary to specify minimum number of hits after final track fit
hiTobTecStepRKTrajectoryFitter = TrackingTools.TrackFitters.RungeKuttaFitters_cff.RKTrajectoryFitter.clone(
    ComponentName = cms.string('hiTobTecStepRKFitter'),
    minHits = 7
)
trackingLowPU.toModify(hiTobTecStepRKTrajectoryFitter, minHits = 8)
trackingPhase1PU70.toModify(hiTobTecStepRKTrajectoryFitter, minHits = 8)

hiTobTecStepRKTrajectoryFitterForLoopers = hiTobTecStepRKTrajectoryFitter.clone(
    ComponentName = cms.string('hiTobTecStepRKFitterForLoopers'),
    Propagator = cms.string('PropagatorWithMaterialForLoopers'),
)

hiTobTecStepRKTrajectorySmoother = TrackingTools.TrackFitters.RungeKuttaFitters_cff.RKTrajectorySmoother.clone(
    ComponentName = cms.string('hiTobTecStepRKSmoother'),
    errorRescaling = 10.0,
    minHits = 7
)
trackingLowPU.toModify(hiTobTecStepRKTrajectorySmoother, minHits = 8)
trackingPhase1PU70.toModify(hiTobTecStepRKTrajectorySmoother, minHits = 8)

hiTobTecStepRKTrajectorySmootherForLoopers = hiTobTecStepRKTrajectorySmoother.clone(
    ComponentName = cms.string('hiTobTecStepRKSmootherForLoopers'),
    Propagator = cms.string('PropagatorWithMaterialForLoopers'),
)

import TrackingTools.TrackFitters.FlexibleKFFittingSmoother_cfi
hiTobTecFlexibleKFFittingSmoother = TrackingTools.TrackFitters.FlexibleKFFittingSmoother_cfi.FlexibleKFFittingSmoother.clone(
    ComponentName = cms.string('hiTobTecFlexibleKFFittingSmoother'),
    standardFitter = cms.string('hiTobTecStepFitterSmoother'),
    looperFitter = cms.string('hiTobTecStepFitterSmootherForLoopers'),
)


# TRACK FITTING
import RecoTracker.TrackProducer.TrackProducer_cfi
hiTobTecStepTracks = RecoTracker.TrackProducer.TrackProducer_cfi.TrackProducer.clone(
    src = 'hiTobTecStepTrackCandidates',
    AlgorithmName = cms.string('tobTecStep'),
    #Fitter = 'tobTecStepFitterSmoother',
    Fitter = 'hiTobTecFlexibleKFFittingSmoother',
    )


# Final selection
import RecoHI.HiTracking.hiMultiTrackSelector_cfi
hiTobTecStepSelector = RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiMultiTrackSelector.clone(
    src='hiTobTecStepTracks',
    useAnyMVA = cms.bool(True),
    GBRForestLabel = cms.string('HIMVASelectorIter13'),
    GBRForestVars = cms.vstring(['chi2perdofperlayer', 'nhits', 'nlayers', 'eta']),
    trackSelectors= cms.VPSet(
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiLooseMTS.clone(
    name = 'hiTobTecStepLoose',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    ), #end of pset
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiTightMTS.clone(
    name = 'hiTobTecStepTight',
    preFilterName = 'hiTobTecStepLoose',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    minMVA = cms.double(-0.2)
    ),
    RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiHighpurityMTS.clone(
    name = 'hiTobTecStep',
    preFilterName = 'hiTobTecStepTight',
    applyAdaptedPVCuts = cms.bool(False),
    useMVA = cms.bool(False),
    minMVA = cms.double(-0.09)
    ),
    ) #end of vpset
    ) #end of clone

import RecoTracker.FinalTrackSelectors.trackListMerger_cfi
hiTobTecStepQual = RecoTracker.FinalTrackSelectors.trackListMerger_cfi.trackListMerger.clone(
    TrackProducers=cms.VInputTag(cms.InputTag('hiTobTecStepTracks')),
    hasSelector=cms.vint32(1),
    selectedTrackQuals = cms.VInputTag(cms.InputTag("hiTobTecStepSelector","hiTobTecStep")),
    copyExtras = True,
    makeReKeyedSeeds = cms.untracked.bool(False),
    )


hiTobTecStep = cms.Sequence(hiTobTecStepClusters*
                          hiTobTecStepSeedLayersTripl*
                          hiTobTecStepTrackingRegionsTripl*
                          hiTobTecStepHitDoubletsTripl*
                          hiTobTecStepHitTripletsTripl*
                          hiTobTecStepSeedsTripl*
                          hiTobTecStepSeedLayersPair*
                          hiTobTecStepTrackingRegionsPair*
                          hiTobTecStepHitDoubletsPair*
                          hiTobTecStepSeedsPair*
                          hiTobTecStepSeeds*
                          hiTobTecStepTrackCandidates*
                          hiTobTecStepTracks*
                          hiTobTecStepSelector*
                          hiTobTecStepQual
                          )



# ### Following are specific for LowPU and/or Phase1PU70, they're collected here to
# ### not to interfere too much with the default configuration
# # For Phase1PU70
# from RecoLocalTracker.SubCollectionProducers.trackClusterRemover_cfi import trackClusterRemover as _trackClusterRemover
# tobTecStepSeedClusters = _trackClusterRemover.clone(
#     maxChi2                                  = 9.0,
#     trajectories                             = "mixedTripletStepTracks",
#     pixelClusters                            = "siPixelClusters",
#     stripClusters                            = "siStripClusters",
#     oldClusterRemovalInfo                    = "mixedTripletStepClusters",
#     overrideTrkQuals                         = 'mixedTripletStep',
#     TrackQuality                             = 'highPurity',
#     minNumberOfLayersWithMeasBeforeFiltering = 0,
# )

# # SEEDING LAYERS
# tobTecStepSeedLayers = cms.EDProducer("SeedingLayersEDProducer",
#     layerList = cms.vstring('TOB1+TOB2', 
#         'TOB1+TEC1_pos', 'TOB1+TEC1_neg', 
#         'TEC1_pos+TEC2_pos', 'TEC2_pos+TEC3_pos', 
#         'TEC3_pos+TEC4_pos', 'TEC4_pos+TEC5_pos', 
#         'TEC5_pos+TEC6_pos', 'TEC6_pos+TEC7_pos', 
#         'TEC1_neg+TEC2_neg', 'TEC2_neg+TEC3_neg', 
#         'TEC3_neg+TEC4_neg', 'TEC4_neg+TEC5_neg', 
#         'TEC5_neg+TEC6_neg', 'TEC6_neg+TEC7_neg'),
#     TOB = cms.PSet(
#         matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
#         skipClusters = cms.InputTag('tobTecStepClusters'),
#         TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTiny'))
#     ),
#     TEC = cms.PSet(
#         matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
#         skipClusters = cms.InputTag('tobTecStepClusters'),
#         #    untracked bool useSimpleRphiHitsCleaner = false
#         useRingSlector = cms.bool(True),
#         TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutTiny')),
#         minRing = cms.int32(5),
#         maxRing = cms.int32(5)
#     )
# )
# trackingPhase1PU70.toModify(tobTecStepSeedLayers,
#     TOB = dict(
#         skipClusters = 'tobTecStepSeedClusters',
#         clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutNone')
#     ),
#     TEC = dict(
#         skipClusters = 'tobTecStepSeedClusters',
#         clusterChargeCut = dict(refToPSet_ = 'SiStripClusterChargeCutNone')
#     ),
# )

# import RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi
# tobTecStepSelector = RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.multiTrackSelector.clone(
#     src = 'tobTecStepTracks',
#     trackSelectors = [
#         RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.looseMTS.clone(
#             name = 'tobTecStepLoose',
#             chi2n_par = 0.25,
#             res_par = ( 0.003, 0.001 ),
#             minNumberLayers = 5,
#             maxNumberLostLayers = 0,
#             minNumber3DLayers = 2,
#             d0_par1 = ( 1.3, 4.0 ),
#             dz_par1 = ( 1.2, 4.0 ),
#             d0_par2 = ( 1.3, 4.0 ),
#             dz_par2 = ( 1.2, 4.0 )
#         ),
#         RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.tightMTS.clone(
#             name = 'tobTecStepTight',
#             preFilterName = 'tobTecStepLoose',
#             chi2n_par = 0.2,
#             res_par = ( 0.003, 0.001 ),
#             minNumberLayers = 5,
#             maxNumberLostLayers = 0,
#             minNumber3DLayers = 2,
#             max_minMissHitOutOrIn = 1,
#             d0_par1 = ( 1.1, 4.0 ),
#             dz_par1 = ( 1.0, 4.0 ),
#             d0_par2 = ( 1.1, 4.0 ),
#             dz_par2 = ( 1.0, 4.0 )
#         ),
#         RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.highpurityMTS.clone(
#             name = 'tobTecStep',
#             preFilterName = 'tobTecStepTight',
#             chi2n_par = 0.15,
#             res_par = ( 0.003, 0.001 ),
#             minNumberLayers = 6,
#             maxNumberLostLayers = 0,
#             minNumber3DLayers = 2,
#             max_minMissHitOutOrIn = 0,
#             d0_par1 = ( 0.9, 4.0 ),
#             dz_par1 = ( 0.8, 4.0 ),
#             d0_par2 = ( 0.9, 4.0 ),
#             dz_par2 = ( 0.8, 4.0 )
#         ),
#     ] #end of vpset
# ) #end of clone

# trackingLowPU.toReplaceWith(TobTecStep, cms.Sequence(
#     tobTecStepClusters*
#     tobTecStepSeedLayers*
#     tobTecStepTrackingRegionsPair*
#     tobTecStepHitDoubletsPair*
#     tobTecStepSeeds*
#     tobTecStepTrackCandidates*
#     tobTecStepTracks*
#     tobTecStep
# ))
# trackingPhase1PU70.toReplaceWith(TobTecStep, cms.Sequence(
#     tobTecStepClusters*
#     tobTecStepSeedClusters*
#     tobTecStepSeedLayers*
#     tobTecStepTrackingRegionsPair*
#     tobTecStepHitDoubletsPair*
#     tobTecStepSeeds*
#     tobTecStepTrackCandidates*
#     tobTecStepTracks*
#     tobTecStepSelector
# ))
