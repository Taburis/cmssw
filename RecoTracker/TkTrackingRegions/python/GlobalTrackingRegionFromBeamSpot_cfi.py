import FWCore.ParameterSet.Config as cms

RegionPsetFomBeamSpotBlock = cms.PSet(
    RegionPSet = cms.PSet(
        precise = cms.bool(True),
       	useMultipleScattering = cms.bool(False),
        nSigmaZ = cms.double(4.0),
        originRadius = cms.double(0.2),
        ptMin = cms.double(0.9),
        beamSpot = cms.InputTag("offlineBeamSpot")
    )
)

RegionPsetFomBeamSpotBlockFixedZ = cms.PSet(
    RegionPSet = cms.PSet(
        precise = cms.bool(True),
       	useMultipleScattering = cms.bool(False),
        originHalfLength = cms.double(21.2),
        originRadius = cms.double(0.2),
        ptMin = cms.double(0.9),
        beamSpot = cms.InputTag("offlineBeamSpot"),
        originRScaling4BigEvts = cms.bool(False),
        minOriginR = cms.double(0),
        ptMinScaling4BigEvts = cms.bool(False),
        maxPtMin = cms.double(1000),
        halfLengthScaling4BigEvts = cms.bool(False),
        minHalfLength = cms.double(0),
        scalingStartNPix = cms.double(20000),
        scalingEndNPix = cms.double(35000)
    )
)

