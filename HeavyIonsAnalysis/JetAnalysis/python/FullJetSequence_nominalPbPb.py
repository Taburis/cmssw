import FWCore.ParameterSet.Config as cms

from HeavyIonsAnalysis.JetAnalysis.jets.HiReRecoJets_HI_cff import *
from RecoHI.HiJetAlgos.HiGenJets_cff import *
from RecoJets.Configuration.GenJetParticles_cff import *
from Configuration.StandardSequences.ReconstructionHeavyIons_cff import voronoiBackgroundPF, voronoiBackgroundCalo

akHiGenJets = cms.Sequence(
    genParticlesForJets +
    ak2HiGenJets +
    ak5HiGenJets)


from HeavyIonsAnalysis.JetAnalysis.jets.akPu2CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs2CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs2PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu2PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu3CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs3CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs3PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu3PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu4CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs4CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs4PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu4PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu5CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs5CaloJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akVs5PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.jets.akPu5PFJetSequence_PbPb_mc_cff import *
from HeavyIonsAnalysis.JetAnalysis.makePartons_cff import *

highPurityTracks = cms.EDFilter("TrackSelector",
                                src = cms.InputTag("hiGeneralTracks"),
                                cut = cms.string('quality("highPurity")'))

from RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi import *
offlinePrimaryVertices.TrackLabel = 'highPurityTracks'

akVs2PFJetAnalyzer.doSubEvent = True
akVs2CaloJetAnalyzer.doSubEvent = True

akVs3PFJetAnalyzer.doSubEvent = True
akVs3CaloJetAnalyzer.doSubEvent = True

akVs4PFJetAnalyzer.doSubEvent = True
akVs4CaloJetAnalyzer.doSubEvent = True

akVs5PFJetAnalyzer.doSubEvent = True
akVs5CaloJetAnalyzer.doSubEvent = True

akVs6PFJetAnalyzer.doSubEvent = True
akVs6CaloJetAnalyzer.doSubEvent = True

akPu1PFJetAnalyzer.doSubEvent = True
akPu1CaloJetAnalyzer.doSubEvent = True

akPu2PFJetAnalyzer.doSubEvent = True
akPu2CaloJetAnalyzer.doSubEvent = True

akPu3PFJetAnalyzer.doSubEvent = True
akPu3CaloJetAnalyzer.doSubEvent = True

akPu4PFJetAnalyzer.doSubEvent = True
akPu4CaloJetAnalyzer.doSubEvent = True

akPu5PFJetAnalyzer.doSubEvent = True
akPu5CaloJetAnalyzer.doSubEvent = True



jetSequences = cms.Sequence(
    akHiGenJets +

    voronoiBackgroundPF+
    voronoiBackgroundCalo+

    akPu2CaloJets +
    akPu2PFJets +
    akVs2CaloJets +
    akVs2PFJets +

    #akPu3CaloJets +
    #akPu3PFJets +
    akVs3CaloJets +
    akVs3PFJets +

    #akPu4CaloJets +
    #akPu4PFJets +
    akVs4CaloJets +
    akVs4PFJets +

    akPu5CaloJets +
    akPu5PFJets +
    akVs5CaloJets +
    akVs5PFJets +

    makePartons +
    highPurityTracks +
    offlinePrimaryVertices +

    akPu2CaloJetSequence +
    akVs2CaloJetSequence +
    akVs2PFJetSequence +
    akPu2PFJetSequence +

    akPu3CaloJetSequence +
    akVs3CaloJetSequence +
    akVs3PFJetSequence +
    akPu3PFJetSequence +

    akPu4CaloJetSequence +
    akVs4CaloJetSequence +
    akVs4PFJetSequence +
    akPu4PFJetSequence +

    akPu5CaloJetSequence +
    akVs5CaloJetSequence +
    akVs5PFJetSequence +
    akPu5PFJetSequence
)
