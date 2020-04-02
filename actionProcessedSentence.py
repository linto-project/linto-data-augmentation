# -*- coding: utf-8 -*-
class actionProcessedSentence:
    # déterminant, nom, adjectif, genre/nombre du nom, syntagme prépositionnel, lemme du verbe, lemme de l'adjectif
    # determinant, noun, adjective, nounFeat, prepSyntagm, verbAnnot, verbLemma, adjectiveLemma
    #def __init__(self, verb, determinant, noun, adjective, followingNominalSyntagms, prepoSyntagm):
    def __init__(self, partsOfSpeech) :

        self.verb = partsOfSpeech['verb']
        self.determinant = partsOfSpeech['determinant']
        self.noun = partsOfSpeech['noun']
        self.adjective = partsOfSpeech['adjective']
        self.prepoSyntagm = partsOfSpeech['prepoSyntagm']
        self.followingNominalSyntagms = partsOfSpeech['followingNominalSyntagms']
        self.adverb = partsOfSpeech['adverb']


    def getVerb(self):
        return self.verb

    def getDeterminant(self):
        return self.determinant

    def getNoun(self):
        return self.noun

    def getAdjective(self):
        return self.adjective

    def getPrepoSyntagm(self):
        return self.prepoSyntagm

    def getFollowingNominalSyntagms(self):
        return self.followingNominalSyntagms

    def getAnnotedPos(self):
        return self.annotedPos

    def getAdverb(self):
        return self.adverb