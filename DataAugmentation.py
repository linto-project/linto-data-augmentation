# -*- coding: utf-8 -*-
from NLPEngine import NLPEngine
from Glawi import Glawi
from loadActionOrInformationGrammar import loadActionOrInformationGrammar
from loadYesOrNoQuestionGrammar import loadYesOrNoQuestionGrammar
import ResourceLoader
from GrammaticalRules import GrammaticalRules
from infoProcessedSentence import infoProcessedSentence
from actionProcessedSentence import actionProcessedSentence
from applyAnnotations import applyAnnotations
from applyAnnotations import applyAnnotationsToYesOrNo
from loadSentencesFile import loadSentencesFile
from synonymGenerator import synonymGenerator
from markdown import MarkDownContent
import glob
import copy
import os

class DataAugmentation:
    def __init__(self, coreNLPDirectory, port, language, glawiBz2FilePath, glawiPklFilePath, lexiconsDirectory, spacyModelPath):

        print("Start NLP engine...")
        self.nlpEngine = NLPEngine(coreNLPDirectory=coreNLPDirectory, port=port, language=language, ip='', spacyModelPath = spacyModelPath)
        ## Load Glawi
        print("Load Glawi...")
        self.glawi = Glawi(glawiBz2FilePath=glawiBz2FilePath, glawiPklFilePath=glawiPklFilePath)

        ## Load grammar rules
        print("Create grammatical rules...")
        grammaticalRules = GrammaticalRules()
        self.actionRules = grammaticalRules.getActionRules()
        self.informationRules = grammaticalRules.getInformationRules()
        self.informationYesOrNoRules = grammaticalRules.getInformationYesOrNoRules()


        ## Load ressources
        print("Loading resources...")

        # ressources to get command type
        informationsKeyWords = list()
        informationsYesOrNoKeyWords = list()
        separator = os.sep

        for ruleFile in glob.glob(lexiconsDirectory + "informations" + separator + "rules" + separator + "*"):
            ResourceLoader.addGrammarResources(ruleFile, self.informationRules)

        for keyWordsFile in glob.glob(lexiconsDirectory + "informations" + separator + "keywords" + separator + "*"):
            ResourceLoader.addKeyWordsResources(keyWordsFile, informationsKeyWords)

        for ruleFile in glob.glob(lexiconsDirectory + "actions" + separator + "rules" + separator + "*"):
            ResourceLoader.addGrammarResources(ruleFile, self.actionRules)

        for ruleFile in glob.glob(lexiconsDirectory + "informations_yesOrNo" + separator + "rules" + separator + "*"):
            ResourceLoader.addGrammarResources(ruleFile, self.informationYesOrNoRules)

        for keyWordsFile in glob.glob(lexiconsDirectory + "informations_yesOrNo" + separator + "keywords" + separator + "*"):
            ResourceLoader.addKeyWordsResources(keyWordsFile, informationsYesOrNoKeyWords)

        self.nlpEngine.setSentenceClassifierKeyWords(informationsKeyWords, informationsYesOrNoKeyWords)

		

    def data_augmentation_from_sentence(self, sentence, limit):

        actionRules = copy.deepcopy(self.actionRules)
        informationRules = copy.deepcopy(self.informationRules)
        informationYesOrNoRules = copy.deepcopy(self.informationYesOrNoRules)

        print("Analyse the sentence with CoreNLP...")
        self.nlpEngine.analyseSentenceCoreNLP(sentence)

        print("Classify sentence...")

        # recognize command type (action or info)
        sentenceType = self.nlpEngine.classifySentence()
        #sentenceType = self.nlpEngine.classifySentence()
        print("Detected sentence type: " + sentenceType[0])

        # get sentence parts of speech
        # sentenceElements = self.nlpEngine.getAllPosInSentence()

        # no file to get synonyms of prepositionnal syntagms
        prepSyntSynonyms = {}

        print("Generate sentences...")

        if sentenceType[0] == "ACTION_COMMAND":

            # get noun synonyms gender and number
            # nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(actionRules['<noun>'])
            # actionRules['<noun>'] = nounSynonymsGenNum

            # get sentence parts of speech
            sentenceElements = self.nlpEngine.getAllPosInSentence()

            # get part of speech for action sentences generation
            sentenceElements = actionProcessedSentence(sentenceElements)

            # get annotations
            print("Get annotations...")
            annotations = applyAnnotations(sentence, sentenceElements)

            # generate new sentences
            return self.action_cmd_data_augmentation(self.glawi.getDictionary(), actionRules, sentenceElements,
                                                     annotations, prepSyntSynonyms, limit)


        elif sentenceType[0] == "INFORMATION_COMMAND":

            # get noun synonyms gender and number
            # nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(informationRules['<noun>'])
            # informationRules['<noun>'] = nounSynonymsGenNum

            # get sentence parts of speech
            sentenceElements = self.nlpEngine.getAllPosInSentence()

            # get part of speech for information sentences generation
            sentenceElements = infoProcessedSentence(sentenceElements)

            print("Get annotations...")
            # get annotations
            annotations = applyAnnotations(sentence, sentenceElements)

            # generate new sentences
            return self.info_cmd_data_augmentation(self.glawi.getDictionary(), informationRules, sentenceElements,
                                                   annotations, prepSyntSynonyms, limit)


        elif sentenceType[0] == "INFORMATION_YES_OR_NO":

            questionType = sentenceType[1]
            #print(questionType)
            # part of speech without interrogative words
            sentenceElements = self.nlpEngine.getSentenceForYesOrNoQuestion()
            depParsing = self.nlpEngine.getPosOfIndexInDepParsing()
            annotations = applyAnnotationsToYesOrNo(sentence)
            return self.infoYesOrNo_cmd_data_augmentation(self.glawi, questionType, depParsing, informationYesOrNoRules, sentenceElements, annotations, limit)

        else :
            return []


    # data augmentation for file
    def data_augmentation_file(self, commandFile, limit):

        generatedCommandFileContent = ''

        actionRules = copy.deepcopy(self.actionRules)
        informationRules = copy.deepcopy(self.informationRules)
        informationYesOrNoRules = copy.deepcopy(self.informationYesOrNoRules)

        # load sentences in linto sentences file
        sentencesInFile = loadSentencesFile(commandFile, self.nlpEngine)

        # dictionnary of intents, sentences and part of speech
        # {intent1 : {sentence1 : {'verb' : verb, 'noun': noun ...}, sentence2 : {'verb': verb ...}, intent2 : ... }
        intentSentPos = sentencesInFile.getIntentSentPosInFile()

        beginningFile = True

        # process each sentence of file
        for intent, sentList in intentSentPos.items():
            intentNum = 0

            if intentNum == 0:
                if beginningFile == True:
                    generatedCommandFileContent = generatedCommandFileContent + "## intent:" + intent + "\n"
                    # prevent printing line break at beginning of file
                    beginningFile = False
                else:
                    generatedCommandFileContent = generatedCommandFileContent + "\n## intent:" + intent + "\n"

            # prevent printing intent multiple times in file
            intentNum = 1

            for sent in sentList:
                similarSentences = []

                generatedCommandFileContent = generatedCommandFileContent + "<!-- Original sentence -->\n" + sent + "\n<!-- Alternative Sentences -->\n"

                print("Analyse the sentence with CoreNLP...")
                self.nlpEngine.analyseSentenceCoreNLP(sent)

                print("Classify sentence...")

                ## recognize command type (action or info)
                sentenceType = self.nlpEngine.classifySentence()
                print(sentenceType)

                if sentenceType[0] == "ACTION_COMMAND" or sentenceType[0] == "INFORMATION_COMMAND":

                    # get sentence parts of speech
                    print("Get parts of speech...")
                    sentencePos = self.nlpEngine.getAllPosInSentence()

                    if sentenceType[0] == "ACTION_COMMAND" :
                        # get part of speech for action sentences generation
                        sentenceElements = actionProcessedSentence(sentencePos)
                    elif sentenceType[0] == "INFORMATION_COMMAND" :
                        # get part of speech for information sentences generation
                        sentenceElements = infoProcessedSentence(sentencePos)
                  
                    # get sentence parts of speech annotations
                    print("Get parts of speech annotations ...")
                    annotations = applyAnnotations(sent, sentenceElements)
                    gramCatAnnotation = annotations.getGramCategoryAnnotation()
                    ## get synonyms
                    print("Get parts of speech synonyms ...")
                    synonymsGeneration = synonymGenerator(self.glawi, gramCatAnnotation, intentSentPos, intent)
                    # get all instances of entities in intent
                    allAnnotationsSynonymsInIntent = synonymsGeneration.getAllAnnotationsInIntent()
                    # get instances of entities as synonyms
                    annotedPosSynonymsList = synonymsGeneration.getAnnotedPosSynonyms()
                    # print(annotedPosSynonymsList)
                    # get non annoted part of speech as synonyms
                    nonAnnotedPosSynonymList = synonymsGeneration.getNonAnnotedPosSynonyms(intent, intentSentPos)
                    # merge both synonym lists
                    synonymListsMerged = synonymsGeneration.mergeSynonymLists(annotedPosSynonymsList,
                                                                              nonAnnotedPosSynonymList)
                    # print(synonymListsMerged)
                    # get synonyms of prepositionnal syntagms in intent
                    prepSyntSynonyms = synonymsGeneration.getPrepoSyntagmSynonyms(intent)


                elif sentenceType[0] == "INFORMATION_YES_OR_NO":

                    # part of speech without interrogative words
                    sentenceElements = self.nlpEngine.getSentenceForYesOrNoQuestion()
                    questionType = sentenceType[1]
                    print(questionType)
                    annotations = applyAnnotationsToYesOrNo(sent)


                if sentenceType[0] == "ACTION_COMMAND":

                    # put synonyms in action ressources
                    print("Put synonyms in ressources ...")
                    actionRules['<verb>'] = synonymListsMerged['verbSynonyms']
                    actionRules['<noun>'] = synonymListsMerged['nounSynonyms']
                    actionRules['<adjective>'] = synonymListsMerged['adjSynonyms']

                    # get noun synonyms gender and number
                    print("Get noun synonyms gender and number ...")
                    nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(actionRules['<noun>'])
                    # put noun synonyms in ressources
                    actionRules['<noun>'] = nounSynonymsGenNum

                    # generate similar sentences
                    print("Generate similar sentences ...")
                    similarSentences = self.action_cmd_data_augmentation(self.glawi.getDictionary(), actionRules,
                                                                         sentenceElements, annotations,
                                                                         prepSyntSynonyms, limit)


                elif sentenceType[0] == "INFORMATION_COMMAND":

                    # put synonyms in information ressources
                    print("Put synonyms in ressources ...")
                    informationRules['<noun>'] = synonymListsMerged['nounSynonyms']
                    informationRules['<adjective>'] = synonymListsMerged['adjSynonyms']

                    # get noun synonyms gender and number
                    print("Get noun synonyms gender and number ...")
                    nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(informationRules['<noun>'])
                    # put noun synonyms in ressources
                    informationRules['<noun>'] = nounSynonymsGenNum

                    # generate similar sentences
                    print("Generate similar sentences ...")
                    similarSentences = self.info_cmd_data_augmentation(self.glawi.getDictionary(), informationRules,
                                                                       sentenceElements, annotations, prepSyntSynonyms,
                                                                       limit)

                elif sentenceType[0] == "INFORMATION_YES_OR_NO" :

                    depParsing = self.nlpEngine.getPosOfIndexInDepParsing()
                    similarSentences = self.infoYesOrNo_cmd_data_augmentation(self.glawi, questionType, depParsing,
                                                                              informationYesOrNoRules, sentenceElements,
                                                                              annotations, limit)
                print("retrieve synonym for: " + sent)
                for similarSentence in similarSentences :
                    if "- " + similarSentence != sent:
                        generatedCommandFileContent = generatedCommandFileContent + "- " + similarSentence + "\n"

        print("File is ready")
        return generatedCommandFileContent

    # data augmentation from string markdown
    def data_augmentation_from_markdown(self, markdown, limit):

        generatedCommandFileContent = ''

        actionRules = copy.deepcopy(self.actionRules)
        informationRules = copy.deepcopy(self.informationRules)
        informationYesOrNoRules = copy.deepcopy(self.informationYesOrNoRules)

        # extracting sentences from a string markdown
        markdownContent = MarkDownContent(markdown)

        # dictionnary of intents, sentences and part of speech
        # {intent1 : {sentence1 : {'verb' : verb, 'noun': noun ...}, sentence2 : {'verb': verb ...}, intent2 : ... }
        intentSentPos = markdownContent.getIntentSentPos(self.nlpEngine)

        beginningFile = True

        # process each sentence of file
        for intent, sentList in intentSentPos.items():
            intentNum = 0

            if intentNum == 0:
                if beginningFile == True:
                    generatedCommandFileContent = generatedCommandFileContent + "## intent:" + intent + "\n"
                    # prevent printing line break at beginning of file
                    beginningFile = False
                else:
                    generatedCommandFileContent = generatedCommandFileContent + "\n## intent:" + intent + "\n"

            # prevent printing intent multiple times in file
            intentNum = 1

            for sent in sentList:
                similarSentences = []

                generatedCommandFileContent = generatedCommandFileContent + "<!-- Original sentence -->\n" + sent + "\n<!-- Alternative Sentences -->\n"

                print("Analyse the sentence with CoreNLP...")
                self.nlpEngine.analyseSentenceCoreNLP(sent)

                print("Classify sentence...")

                ## recognize command type (action or info)
                sentenceType = self.nlpEngine.classifySentence()
                print(sentenceType)

                if sentenceType[0] == "ACTION_COMMAND" or sentenceType[0] == "INFORMATION_COMMAND":

                    # get sentence parts of speech
                    print("Get parts of speech...")
                    sentencePos = self.nlpEngine.getAllPosInSentence()

                    if sentenceType[0] == "ACTION_COMMAND":
                        # get part of speech for action sentences generation
                        sentenceElements = actionProcessedSentence(sentencePos)
                    elif sentenceType[0] == "INFORMATION_COMMAND":
                        # get part of speech for information sentences generation
                        sentenceElements = infoProcessedSentence(sentencePos)

                    # get sentence parts of speech annotations
                    print("Get parts of speech annotations ...")
                    annotations = applyAnnotations(sent, sentenceElements)
                    gramCatAnnotation = annotations.getGramCategoryAnnotation()
                    ## get synonyms
                    print("Get parts of speech synonyms ...")
                    synonymsGeneration = synonymGenerator(self.glawi, gramCatAnnotation, intentSentPos, intent)
                    # get all instances of entities in intent
                    allAnnotationsSynonymsInIntent = synonymsGeneration.getAllAnnotationsInIntent()
                    # get instances of entities as synonyms
                    annotedPosSynonymsList = synonymsGeneration.getAnnotedPosSynonyms()
                    # print(annotedPosSynonymsList)
                    # get non annoted part of speech as synonyms
                    nonAnnotedPosSynonymList = synonymsGeneration.getNonAnnotedPosSynonyms(intent, intentSentPos)
                    # merge both synonym lists
                    synonymListsMerged = synonymsGeneration.mergeSynonymLists(annotedPosSynonymsList,
                                                                              nonAnnotedPosSynonymList)
                    # print(synonymListsMerged)
                    # get synonyms of prepositionnal syntagms in intent
                    prepSyntSynonyms = synonymsGeneration.getPrepoSyntagmSynonyms(intent)


                elif sentenceType[0] == "INFORMATION_YES_OR_NO":

                    # part of speech without interrogative words
                    sentenceElements = self.nlpEngine.getSentenceForYesOrNoQuestion()
                    questionType = sentenceType[1]
                    print(questionType)
                    annotations = applyAnnotationsToYesOrNo(sent)

                # generate sentences
                if sentenceType[0] == "ACTION_COMMAND":

                    # put synonyms in action ressources
                    print("Put synonyms in ressources ...")
                    actionRules['<verb>'] = synonymListsMerged['verbSynonyms']
                    actionRules['<noun>'] = synonymListsMerged['nounSynonyms']
                    actionRules['<adjective>'] = synonymListsMerged['adjSynonyms']

                    # get noun synonyms gender and number
                    print("Get noun synonyms gender and number ...")
                    nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(actionRules['<noun>'])
                    # put noun synonyms in ressources
                    actionRules['<noun>'] = nounSynonymsGenNum

                    # generate similar sentences
                    print("Generate similar sentences ...")
                    similarSentences = self.action_cmd_data_augmentation(self.glawi.getDictionary(), actionRules,
                                                                         sentenceElements, annotations,
                                                                         prepSyntSynonyms, limit)

                elif sentenceType[0] == "INFORMATION_COMMAND":

                    # put synonyms in information ressources
                    print("Put synonyms in ressources ...")
                    informationRules['<noun>'] = synonymListsMerged['nounSynonyms']
                    informationRules['<adjective>'] = synonymListsMerged['adjSynonyms']

                    # get noun synonyms gender and number
                    print("Get noun synonyms gender and number ...")
                    nounSynonymsGenNum = self.glawi.getNounSynonymsGenderNumber(informationRules['<noun>'])
                    # put noun synonyms in ressources
                    informationRules['<noun>'] = nounSynonymsGenNum

                    # generate similar sentences
                    print("Generate similar sentences ...")
                    similarSentences = self.info_cmd_data_augmentation(self.glawi.getDictionary(), informationRules,
                                                                       sentenceElements, annotations, prepSyntSynonyms,
                                                                       limit)

                elif sentenceType[0] == "INFORMATION_YES_OR_NO":

                    depParsing = self.nlpEngine.getPosOfIndexInDepParsing()
                    similarSentences = self.infoYesOrNo_cmd_data_augmentation(self.glawi, questionType, depParsing,
                                                                              informationYesOrNoRules, sentenceElements,
                                                                              annotations, limit)

                for similarSentence in similarSentences:
                    if "- " + similarSentence != sent:
                        generatedCommandFileContent = generatedCommandFileContent + "- " + similarSentence + "\n"

        return generatedCommandFileContent



    # data augmentation for action type command
    def action_cmd_data_augmentation(self, dico, actionRules, sentenceElements, annotations, prepSyntSynonyms, limit):
        similarSentences = []

        for i in range(limit):
            try:
                loadActionGrammar = loadActionOrInformationGrammar(dico, actionRules, sentenceElements, annotations, prepSyntSynonyms)
                generatedSentence = loadActionGrammar.generateSimilarExpre('<start>')
                similarSentences.append(generatedSentence.strip())
            except:
                pass

        similarSentences = set(similarSentences)

        return similarSentences

    # data augmentation for information type command
    def info_cmd_data_augmentation(self, dico, infoRules, sentenceElements, annotations, prepSyntSynonyms, limit):
        similarSentences = []

        for i in range(limit):
            try:
                if sentenceElements.getNoun() != "":
                    loadInfoGrammar = loadActionOrInformationGrammar(dico, infoRules, sentenceElements, annotations, prepSyntSynonyms)
                    generatedSentence = loadInfoGrammar.generateSimilarExpre('<start>')
                    similarSentences.append(generatedSentence.strip())
                else:
                    pass
            except:
                pass

        similarSentences = set(similarSentences)

        return similarSentences


    def infoYesOrNo_cmd_data_augmentation(self, glawi, questionType, depParsing, infoYesOrNoRules, sentenceElements, annotations, limit):
        similarSentences = []

        for i in range(limit):
            try :
                loadYesOrNoGrammar = loadYesOrNoQuestionGrammar(glawi, questionType, depParsing, infoYesOrNoRules, sentenceElements, annotations)
                generatedSentence = loadYesOrNoGrammar.generateSimilarExpression('<start>')
                if generatedSentence != "" :
                    similarSentences.append(generatedSentence.strip())
            except :
                pass

        similarSentences = set(similarSentences)

        return similarSentences


    def stopDASystem(self):
        self.nlpEngine.stopNLPEngine()

