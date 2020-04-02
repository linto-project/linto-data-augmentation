# -*- coding: utf-8 -*-
# Simple usage
# https://github.com/Lynten/stanford-corenlp
from stanfordcorenlp import StanfordCoreNLP
import re
import os
import subprocess
from applyAnnotations import applyAnnotations
import spacy



################ RECONNAISSANCE DU TYPE DE COMMANDE ET APPEL DE CORENLP 

class NLPEngine:

    def __init__(self, coreNLPDirectory, port, language, ip, spacyModelPath):

        if ip == '' or ip == None:
            ip = 'http://localhost'

        #nlp = StanfordCoreNLP(r'D:\Users\User\Desktop\stanford-corenlp-full-2018-10-05',memory='8g', lang='fr')
        try:

            cwd = os.getcwd()
            os.chdir(coreNLPDirectory)
            self.process = subprocess.Popen(
                ['java', '-Xmx4G', '-cp', '*', 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-serverProperties',
                 'StanfordCoreNLP-' + language + '.properties', '-port', str(port), '-timeout', '15000', '&'])
            #os.system(cmd)
            os.chdir(cwd)
        except:
            print('CoreNLPServer all ready started !')

        self.nlp = StanfordCoreNLP(ip, port = port, lang = language[:2])
        #props = {'annotators': 'tokenize,ssplit,pos,depparse','pipelineLanguage':'fr','outputFormat':'text'}
        #print(self.nlp.annotate("bonjour tout le monde ici", props))

        self.informationKeyWords = list()

        # load Spacy
        self.spacyNlp = spacy.load(spacyModelPath)


    def stopNLPEngine(self):
        self.nlp.close()
        self.process.kill()

    def analyseSentenceCoreNLP(self, sentence):
        # phrase annotée
        self.annotedSent = sentence
        # enlever les annotations de la phrase originale
        notAnnotedSent = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', sentence)
        self.notAnnotedSent = re.sub(r'(- (.*))', r'\2', notAnnotedSent)
        # print(self.notAnnotedSent)

        # analyse des part of speech
        self.pos = self.nlp.pos_tag(self.notAnnotedSent)
        print(self.pos)

        # analyse des dépendances syntaxiques
        self.dp = self.nlp.dependency_parse(self.notAnnotedSent)

    ####### RECONNAISSANCE TYPE COMMANDE (information/action)

    def setSentenceClassifierKeyWords(self, informationKeyWords, infoYesOrNoKeyWords):
        self.informationKeyWords = informationKeyWords
        self.infoYesOrNoKeyWords = infoYesOrNoKeyWords
    

    # déterminer si la commande est une demande d'information ou d'action
    def classifySentence(self):

        # variable qui retourne le résultat trouvé action ou information
        commandType = ("", "")
        # booléen qui arrête la recherche si au moins un pattern d'information est trouvé
        infoFoundOnce = False
        # déterminer si c'est une commande d'action (effectuer une action)
        action = re.search("(\[(.+)\]\(action_\w+\))", self.annotedSent)
        
        # si c'est bien une action, l'indiquer dans la variable commandType
        if action:
            commandType = ("ACTION_COMMAND", "")

        # sinon si ce n'est pas une commande d'action
        else:
            # chercher les mots clés des commandes d'information
            for keyWord in self.informationKeyWords :
                checkInfoKeyWord = re.search("^" + keyWord, self.notAnnotedSent)
                if checkInfoKeyWord :
                    commandType = ("INFORMATION_COMMAND", "")
            if commandType == ("", "") :
                if self.pos[0][1] == "NOUN" :
                    commandType = ("INFORMATION_COMMAND", "")
            if commandType == ("", "") :
                commandType = self.checkIfYesOrNoQuestion()
            
        return commandType

    ####### RECUPERATION DES PART OF SPEECH

    # récupérer le verbe via son annotation (action_??)
    def getNonAnnotedVerbAction(self):

        # chercher le mot accompagné de l'annotation (action_??) dans la phrase annotée
        actionVerbSearch = re.search("(\[(.+)\]\(action_\w+\))", self.annotedSent)
        if actionVerbSearch:
            actionVerbNonAnnoted = actionVerbSearch.group(2)
        else:
            actionVerbNonAnnoted = ""

        return actionVerbNonAnnoted

    # analyse des dépendances syntaxiques et part of speech de CoreNlp
    # récupérer un part of speech lié à un autre part of speech par une relation spécifique (ex: déterminant d'un nom via la relation "det")
    def getPos(self, indexOfInitialPos, grammaticalRelation):

        try:
            # chercher l'index du mot dépendant à partir de -> l'index du mot tête donné et de la relation syntaxique donnée
            # ex: ('det', 3, 2) -> à partir de 'det' et index 3 (tête) -> récupérer index 2 (dépendant)
            for l in self.dp:
                if l[0] == grammaticalRelation and l[1] == indexOfInitialPos + 1:
                    indexOfposSearched = l[2] - 1
            # chercher le mot auquel l'index correspond dans les part of speech
            # [('débute', 'VERB'), ('le', 'DET'), ('chronomètre', 'NOUN')] -> "le"
            for l in self.pos:
                foundPos = self.pos[indexOfposSearched][0]

        except UnboundLocalError:

            foundPos = ""

        return foundPos

    # récupérer tous les noms de la phrase
    def getAllNouns(self):

        # liste des mots régulièrement mal reconnus par CoreNlp
        falseNoun = ["est", "sont"]
        verb = self.getNonAnnotedVerbAction()
        nounAndIndex = {}
        # chercher tous les noms dans les part of speech
        for i, l in enumerate(self.pos, start=0):
            if l[1] == 'NOUN':
                noun = l[0]
                # les récupérer {nom : index}
                # récupérer le nom seulement s'il n'est pas identifié comme une erreur de coreNLP
                if noun not in falseNoun:
                    if noun != verb:
                        nounAndIndex[noun] = i

        # supprimer les noms apparaissant dans une relation "case" (ils font partie d'un syntagme prépositionnel)
        for key, value in nounAndIndex.copy().items():
            for l in self.dp:
                if l[1] == value + 1 and l[0] == 'case':
                    notNeededNoun = self.pos[value][0]
                    del nounAndIndex[notNeededNoun]

        return nounAndIndex

    # récupérer les déterminants et adjectifs correspondant aux noms
    def getAllNominalSyntagms(self):

        falseDet = ['sont']
        verb = self.getNonAnnotedVerbAction()
        cpt = 1
        allNoun = self.getAllNouns()
        allNominalSyntagms = {}
        for key, value in allNoun.items():
            det = self.getPos(value, 'det')
            # vérifier si le déterminant en est bien un
            if det in falseDet:
                det = ""
            # si on ne trouve pas de déterminant, on cherche un adjectif possessif (ex: "mon mail")
            if det == "":
                det = self.getPos(value, 'nmod:poss')
            adj = self.getPos(value, 'amod')
            # ne pas récupérer l'adjectif si c'est le verbe identifié par tock
            if adj == verb:
                adj = ""
            # récupérer {1: ('la', 'lumière', 'rouge') 2:('le', 'salon', 'vert')}
            allNominalSyntagms[cpt] = (det, key, adj)
            cpt = cpt + 1
        return allNominalSyntagms

    # récupérer le syntagme nominal principal ("la chanson la bohème" -> "la chanson")
    def getPrincipalNominalSyntagm(self):

        allNominalSyntagms = self.getAllNominalSyntagms()
        # notNeededDet = ['quel','quels','quelle','quelles']
        # on récupère le premier syntagme apparu dans la phrase
        if len(allNominalSyntagms) != 0:
            determinant = allNominalSyntagms[1][0]
            # if determinant in notNeededDet :
            if determinant == "quel":
                determinant = "le"
            elif determinant == "quelle":
                determinant = "la"
            elif determinant == "quels" or determinant == "quelles":
                determinant = "les"
            noun = allNominalSyntagms[1][1]
            adjective = allNominalSyntagms[1][2]
            principalNominalSyntagm = (determinant, noun, adjective)
        else:
            principalNominalSyntagm = ("", "", "")

        return principalNominalSyntagm

    # récupérer les syntagmes nominaux qui suivent le syntagme nominal principal
    # "la chanson la foule" -> "la foule"
    def getFollowingNominalSyntagms(self):

        allNominalSyntagms = self.getAllNominalSyntagms()
        followingNominalSyntagms = ""

        if len(allNominalSyntagms) != 0:
            # récupérer tous les syntagmes nominaux qui viennent après le premier
            for key, value in allNominalSyntagms.items():
                if key > 1:
                    determinant = allNominalSyntagms[key][0]
                    noun = allNominalSyntagms[key][1]
                    adjective = allNominalSyntagms[key][2]

                    # les concaténer dans une string
                    # les SN qui suivent le principal ne devraient pas être modifiés (remplacés par des synonymes -> "la bohème" est une chanson)
                    if adjective == "":
                        followingNominalSyntagms = followingNominalSyntagms + determinant + " " + noun + " "
                    else:
                        followingNominalSyntagms = followingNominalSyntagms + determinant + " " + noun + " " + adjective
        else:
            followingNominalSyntagms = ""

        return followingNominalSyntagms

    # vérifier si un token est un nombre
    def checkIfNumber(self, word):

        checkIfNum = False
        for p in self.pos:
            if p[0] == word:
                if p[1] == "NUM":
                    checkIfNum = True

        return checkIfNum

    # récupérer les modifieurs numériques (75 -> pourcent )
    def getNumericModifierInPrepSyntagm(self, number):

        # récupérer l'analyse en dépendance de Spacy
        sentence = self.spacyNlp(self.notAnnotedSent)
        depAnalysis = []
        for token in sentence:
            dep = (token.text.lower(), token.dep_, token.head.text.lower())
            depAnalysis.append(dep)

        numericModifier = ""

        for dep in depAnalysis:
            # si c'est le cas, récupérer son modifieur (ex: pourcent)
            if dep[0] == number and dep[1] == "nummod":
                numericModifier = dep[2]

        return numericModifier

    # récupérer les annotations pour les syntagmes prépositionnaux
    # def getPrepSyntagmAnnotations(self, prepoSyntFromCoreNlp) :

    #     annotation = "no_annotation"
    #     # nouveau dictionnaire des SP
    #     newSyntPrepDic = {}
    #     # chercher tous les mots annotés dans la phrase d'entrée
    #     regexAnnotWords = r'(\[(\S+?(?: \S+)*)\]\((\w+)\))'
    #     # liste des mots annotés
    #     annotedWords = re.findall(regexAnnotWords, self.annotedSent)
    #     print(annotedWords)
    #     # ne garder qu'une anntation du SP comme référence (de le [mois](time) [prochain](next_time) -> time)
    #     stopFirstAnnot = True

    #     # pour chaque syntagme prépositionnel récupéré avec CoreNLP
    #     for index,prepSynt in prepoSyntFromCoreNlp.items() :
    #         # pour chaque mot dans le syntagme prépostionnel
    #         for word in prepSynt :
    #             # pour chaque mot dans la phrase d'entrée
    #             for w in annotedWords :
    #                 # groupe capturant correspondant à la version du mot avec le markdown (ex: [jour](time) )
    #                 annotedWord = w[0]
    #                 # groupe capturant correspondant à la version du mot débarassée du markdown (ex: [jour](time) --> jour)
    #                 nonAnnotedWord = w[1]
    #                 # groupe capturant correspondant à l'annotation (ex: [jour](time) -> time)
    #                 wordAnnotation = w[2]
    #                 # si le mot annoté est égal au mot du syntagme prépositionnel CoreNLP
    #                 if word == nonAnnotedWord and stopFirstAnnot == True : #and annotedWord not in newSyntPrep:
    #                     annotation = wordAnnotation
    #                     stopFirstAnnot = False
    #                 elif word == nonAnnotedWord and stopFirstAnnot == False :
    #                     annotation = "no_annotation"
    #                     stopFirstAnnot = True

    #         # compléter le nouveau dictionnaire avec les mots annotés
    #         newSyntPrepDic[str(index) + "_" + annotation] = prepSynt

    #     return newSyntPrepDic

    # récupérer les annotations des SP
    def getPrepSyntagmAnnotations(self, prepoSyntFromCoreNlp):

        # nouveau SP
        newSyntPrep = []
        # nouveau dictionnaire des SP
        newSyntPrepDic = {}
        # chercher tous les mots annotés dans la phrase d'entrée
        regexAnnotWords = r'(\[(\S+?(?: \S+)*)\]\((\w+)\))'
        # liste des mots annotés
        annotedWords = re.findall(regexAnnotWords, self.annotedSent)

        # transformer le résultat de 'annotedWords' en dictionnaire
        annotWordDic = {}
        for annot in annotedWords:
            # science : ([science](type_sciences), type_sciences)
            annotWordDic[annot[1]] = (annot[0], annot[2])

        # pour chaque syntagme prépositionnel récupéré avec CoreNLP
        for index, prepSynt in prepoSyntFromCoreNlp.items():
            # pour chaque mot dans le syntagme prépostionnel
            for word in prepSynt:
                if word in annotWordDic:
                    annotedWord = annotWordDic[word][0]
                    newSyntPrep.append(annotedWord)
                elif word not in annotWordDic:
                    newSyntPrep.append(word)

            # compléter le nouveau dictionnaire avec les mots annotés
            newSyntPrepDic[index] = tuple(newSyntPrep)
            newSyntPrep = []

        return newSyntPrepDic

    # récupérer les syntagmes prépositionaux dans leur ordre d'apparition
    def getPrepSyntagm(self):

        cpt = 1
        prepoSyntagmIndex = {}
        prepoSyntagm = {}
        try:
            # chercher les couples de mots ayant une relation "case" dans les dépendances syntaxiques
            for line in self.dp:
                if line[0] == "case":
                    # prepoSyntagmIndex[cpt] = (line[1],line[2])
                    # adp: nom -> 'dans':'salon'
                    prepoSyntagmIndex[line[1]] = line[2]

            # attribuer un numéro à chaque couple (utile pour garder un ordre d'apparition mais pas utilisé?)
            # dictionnaire --> 1 : (index de "dans", index de "salon")
            for key, value in list(prepoSyntagmIndex.items()):
                prepoSyntagm[cpt] = (key, value)
                cpt = cpt + 1

            # récupérer l'index de l'adjectif associé au nom (s'il y en a un)
            for key, value in list(prepoSyntagm.items()):
                for line in self.dp:
                    # utiliser la relation "amod"
                    if line[0] == "amod" and line[1] == value[0]:
                        # 1 : (index de "dans", index de "salon", index de "jaune")
                        prepoSyntagm[key] = (value, line[2])
                        cpt = cpt + 1
                        # savoir si l'adjectif est avant ou après le nom
                        if line[1] > line[2]:
                            reversedNounAdj = True
                        else:
                            reversedNounAdj = False

            # récupérer les mots qui correspondent aux index récupérés précedemment
            for key, value in list(prepoSyntagm.items()):

                # vérifier s'il y a un adjectif
                if str(value).count(",") + 1 == 3:

                    notNeededDeterminants = ["quel", "Quel", "quelle", "Quelle", "quels", "Quels", "quelles", "Quelles"]
                    # récupérer ADP (de, dans...) , déterminant, nom, adjectif
                    adp = self.pos[value[0][1] - 1][0]
                    determinant = self.pos[value[0][1]][0]
                    if determinant in notNeededDeterminants:
                        determinant = "le/la/les"
                    noun = self.pos[value[0][0] - 1][0]
                    adjective = self.pos[value[1] - 1][0]

                    # vérifier si le token de noun est un nom commun ou un nombre
                    checkIfNum = self.checkIfNumber(noun)
                    # si c'est le cas, chercher s'il est accompagné d'un modifieur (ex: 3 bonbons, 90 pourcents)
                    if checkIfNum == True:
                        numModif = self.getNumericModifierInPrepSyntagm(noun)
                    else:
                        numModif = ""

                    # inverser les emplacements nom et adjectif si c'est le cas dans la phrase d'entrée
                    # ex: "le bel ordinateur" / "l'ordinateur noir"
                    if reversedNounAdj == True:

                        # sans déterminant ("de bonne musique")
                        if determinant == noun:
                            prepoSyntagm[key] = (adp, adjective, noun)
                        # avec déterminant
                        else:
                            prepoSyntagm[key] = (adp, determinant, adjective, noun)

                    # sinon garder un modèle nom suivi d'adjectif
                    elif reversedNounAdj == False:

                        # sans déterminant (niveau [de pollution maximal])
                        if determinant == noun:
                            # vérifier s'il y a un modifieur (ex: 90 bons pourcents)
                            if numModif == "":
                                prepoSyntagm[key] = (adp, noun, adjective)
                            else:
                                prepoSyntagm[key] = (adp, noun, adjective, numModif)
                        # avec déterminant
                        else:
                            prepoSyntagm[key] = (adp, determinant, noun, adjective)

                # s'il n'y pas d'adjectif
                else:
                    adp = self.pos[value[1] - 1][0]
                    determinant = self.pos[value[1]][0]
                    noun = self.pos[value[0] - 1][0]
                    numModif = self.getNumericModifierInPrepSyntagm(noun)

                    # vérifier s'il y a un déterminant ou non (cas de "à Toulouse")
                    if determinant == noun:
                        # vérifier s'il y a un modifieur (ex: 90 pourcent)
                        if numModif == "":
                            prepoSyntagm[key] = (adp, noun)
                        else:
                            prepoSyntagm[key] = (adp, noun, numModif)
                    else:
                        prepoSyntagm[key] = (adp, determinant, noun)



        except IndexError:
            prepoSyntagm = {}

        prepoSyntagm = self.getPrepSyntagmAnnotations(prepoSyntagm)
        # print(self.getPrepSyntagmAnnotations(prepoSyntagm))

        return prepoSyntagm

    # récupérer un adverbe de fin de phrase (ex : "maintenant", "demain", "aujourd'hui")
    # qui apparaissent sans relation "case" (syntagme prépositionnel)
    def getAdverb(self):

        adverb = ""
        posLen = len(self.pos)

        # chercher l'adverbe
        for i, p in enumerate(self.pos, start=0):
            if p[1] == 'ADV' and i == posLen - 1:
                adverb = p[0]
                for j in self.dp:
                    if j[0] == "case" and j[1] == posLen:
                        adverb = ""
                    # else :
                    #     adverb = p[0]

        return adverb

    # récupérer un dictionnaire contenant tous les part of speech d'une phrase
    def getAllPosInSentence(self):

        verb = self.getNonAnnotedVerbAction()

        principalNominalSyntagm = self.getPrincipalNominalSyntagm()
        determinant = principalNominalSyntagm[0]
        noun = principalNominalSyntagm[1]
        adjective = principalNominalSyntagm[2]

        followingNominalSyntagms = self.getFollowingNominalSyntagms()

        prepoSyntagm = self.getPrepSyntagm()

        adverb = self.getAdverb()

        posInSentence = {"verb": verb, "determinant": determinant, "noun": noun, "adjective": adjective,
                         "followingNominalSyntagms": followingNominalSyntagms, "prepoSyntagm": prepoSyntagm,
                         "adverb": adverb}

        return posInSentence

    # récupérer tous les part of speech d'une phrase type "interrogation totale" (réponse oui/non)
    # def getAllPosInGeneralQuestions(self) :

    #     # dictionnaire des part of speech de la question
    #     posInGeneralQuestion = {}
    #     # dictionnaire du nombre actuel de chaque part of speech
    #     # ex: {det : 1, noun : 2 ...}
    #     numberOfgramCat = {}
    #     for word in self.pos :
    #         gramCat = word[1].lower()
    #         word = word[0]
    #         if gramCat not in numberOfSpecificPos :
    #             numberOfgramCat[gramCat] = 1
    #             posInGeneralQuestion[gramCat + "_1"] = word
    #         else :
    #             number = str(numberOfgramCat[gramCat])
    #             gramCat = gramCat + "_" + number
    #             posInGeneralQuestion[gramCat] = word
    #             newGramCatNumber = numberOfgramCat[gramCat] + 1
    #             numberOfgramCat[gramCat] = newGramCatNumber

    #     return posInGeneralQuestion

    # pré-traiter la phrase information en enlevant les expressions de début de phrase totale
    def removeYesNoExpressions(self) :
    #def getEstCeQueSentence(self) :

        indirectYesOrNo = False
        # vérifier si la commande débute par "est-ce que", "dis moi si..."
        for keyWord in self.infoYesOrNoKeyWords :
            if re.search("^" + keyWord, self.notAnnotedSent) != None:
                indirectYesOrNo = True
                break
            # if keyWord in self.notAnnotedSent :
            #     indirectYesOrNo = True

        #estCeQue = re.search('^est-ce (qu\'|que)',self.notAnnotedSent)

        # récupérer la phrase qui suit "est-ce que"
        conjunctions = ["que","qu'", "si"]
        cpt = 0
        newSent = []

        if indirectYesOrNo :
            # récupérer l'index où commence la phrase sans l'expression
            for word in self.pos :
                cpt = cpt + 1
                if word[0] in conjunctions :
                    sconjIndex = cpt

            # récupérer les tokens qui suivent l'expression
            for i in range(sconjIndex,len(self.pos)) :
                newSent.append(self.pos[i])

        else :
            newSent = []
     
        return newSent


    def getSentenceForYesOrNoQuestion(self) :

        # vérifier si la phrase est une interrogation totale
        yesOrNoSent = self.removeYesNoExpressions()
        if len(yesOrNoSent) == 0 :
            yesOrNoSent = self.pos

        return yesOrNoSent


    # vérifier si la commande information correspond à un patron lexico-syntaxique connu
    def checkIfYesOrNoQuestion(self) :

        # vérifier si la phrase est de type "est-ce que"
        yesOrNoSent = self.getSentenceForYesOrNoQuestion()
        # récupérer les catégories grammaticales dans une string
        gramCat = ""
        for couple in yesOrNoSent :
            gramCat = gramCat + couple[1] + " "
        #print(gramCat)
        # vérifier si la phrase correspond aux règles syntaxiques d'une question totale

        # (est-ce que) la salle est libre
        # (est-ce que) la salle de réunion est libre
        #pattern1 = re.search('DET NOUN (AUX|VERB)(?! PRON)', gramCat)
        pattern1 = re.search('^DET NOUN( ADJ)?( ADP( DET)? NOUN( ADJ)?)* (AUX|VERB)(?! PRON)', gramCat)
        # (est-ce que) il neige
        pattern2 = re.search('^PRON (AUX|VERB)', gramCat) #^(PRON|PROPN) (AUX|VERB)(?! VERB)
        # la salle (de réunion) est-elle libre
        pattern3 = re.search('^(DET NOUN( ADJ)?|PROPN)( ADP( DET)? (NOUN|PROPN)( ADJ)?)* (AUX|VERB) PRON', gramCat)
        # pleut-il
        pattern4 = re.search('^(VERB|AUX) PRON', gramCat)
        # (est-ce) qu'il va neiger -> deux verbes qui se suivent (semi-auxiliaire + verbe)
        #pattern5 = re.search('^PRON (AUX|VERB)', gramCat)

        if pattern1 :
            # syntagme nominal + verbe
            commandType = ("INFORMATION_YES_OR_NO", "SN_V")

        elif pattern2 :
            # pronom + verbe
            commandType = ("INFORMATION_YES_OR_NO", "PRON_V")

        elif pattern3 :
            # syntagme nominal + verbe + pronom
            # vérifier si le déterminant est un déterminant interrogatif
            det = self.pos[0][0]
            detInterro = ["quel", "quels", "quelle", "quelles"]
            # dans ce cas, traiter la phrase comme une commande info
            if det in detInterro :
                commandType = ("INFORMATION_COMMAND", "")
            else :
                commandType = ("INFORMATION_YES_OR_NO", "SN_V_PRON")

        elif pattern4 :
            # verbe + pronom
            commandType = ("INFORMATION_YES_OR_NO", "V_PRON")

        # elif pattern5 :
        #     # pronom + semi-auxiliaire + verbe
        #     commandType = ("INFORMATION_YES_OR_NO", "PRON_V_V")
        else :

            # générer les autres types de commande d'information
            #commandType = ("INFORMATION_COMMAND", "")
            commandType = ("", "")

        return commandType


    def getPosOfIndexInDepParsing(self) :

        dpTriplet = []
        headWord = ""
        dependentWord = ""
        for d in self.dp :
            syntRelation = d[0]
            headIndex = d[1]
            dependentIndex = d[2]
            
            for index, word in enumerate(self.pos, start=1):
                if index == headIndex :
                    headWord = word[0]
                elif index == dependentIndex :
                    dependentWord = word[0] 

            dpTriplet.append((syntRelation, headWord, dependentWord))

        return dpTriplet



