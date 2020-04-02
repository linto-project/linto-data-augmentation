# -*- coding: utf-8 -*-
# https://github.com/Ragnarok540/RandomGrammar
# basé sur https://github.com/bertez/treegrammar
import random
import re
import os
import xml.etree.ElementTree as ET
from Glawi import Glawi
from applyAnnotations import applyAnnotations
from infoProcessedSentence import infoProcessedSentence
from actionProcessedSentence import actionProcessedSentence


########## Parser les règles et générer les nouvelles commandes

class loadActionOrInformationGrammar:
   
    # dictionnaire Glawi, catégorie de règles utilisées
    def __init__(self, dico, ruleSet, sentenceElements, annotations, prepSyntSynonyms):

        self.grammar = {}
        self.regex = '<\w+>'
        for rule in ruleSet:
            self.addRule(rule, ruleSet[rule])

        self.verb = sentenceElements.getVerb()
        self.determinant = sentenceElements.getDeterminant()
        self.noun = sentenceElements.getNoun()
        self.adjective = sentenceElements.getAdjective()
        self.followingNominalSyntagms = sentenceElements.getFollowingNominalSyntagms()
        #self. prepoSyntagm = ""
        prepoSyntagm = sentenceElements.getPrepoSyntagm()
        if len(prepoSyntagm) != 0 :
            self.prepoSyntagm = prepoSyntagm
        else :
            self.prepoSyntagm = {}

        self.adverb = sentenceElements.getAdverb()
  
        self.posAnnotations = annotations
        self.dico = dico
        self.prepSyntSynonyms = prepSyntSynonyms

    

    def addRule(self, ruleName, ruleContent):
        if re.match(self.regex, ruleName) == None:
            raise Exception('Malformed rule name.')
        if type(ruleContent) is not list:
            raise Exception('Rule content must be a list.')
        if ruleName not in self.grammar:
            self.grammar[ruleName] = ruleContent
        else:
            raise Exception('Rule already exists.')
        


    ## RECUPERATION DES TRAITS MORPHOSYNTAXIQUES DES OBJETS GLAWI (lemme, genre, nombre...)

    # récupérer le genre et le nombre d'un mot dans un objet Glawi
    def getGlawiInputWordGenderNumber(self, word, wordType):

        try :
            glawiObject = self.dico[word + "_" + wordType]
            gender = glawiObject["gender"]
            number = glawiObject["number"]

            if gender == "":
                gender = "m"

            if number == "":
                number = "s"

            wordGenderNumber = "gender=" + gender + "|number=" + number

        except KeyError :

            wordGenderNumber = "gender=|number="

        return wordGenderNumber


    # récupérer le lemme d'un mot dans Glawi
    def getGlawiInputWordLemma(self, word, wordType):

        try :
            glawiObjectWord = self.dico[word + "_" + wordType]
            wordLemma = glawiObjectWord["lemma"]

            if wordLemma == "" :
                wordLemma = word
        except KeyError :
            wordLemma = word

        return wordLemma


    ## CHOIX ALEATOIRE DE CERTAINES PARTIES DU DISCOURS

    # choisir un adjectif dans la liste des ressources
    def randomAdjective(self):

        randomAdjective = ()
        # choisir un adjectif dans la liste des ressources <adjective>
        newValue = random.sample(self.grammar['<adjective>'], 1)[0]
        # si l'élément original_$ est choisi, c'est qu'il s'agit de l'adjectif d'origine
        if newValue == "original_$":
            adjective = self.adjective
            checkOriginAdj = "!original_adjective!"
        # sinon il s'agit d'un adjectif synonyme
        else:
            adjective = newValue
            checkOriginAdj = "!synonym_adjective!"
        
        randomAdjective = (adjective, checkOriginAdj)

        return randomAdjective


    # choisir aléatoirement un nom dans la liste des noms en ressource
    def randomNoun(self):
        
        randomNoun = ()
        newValue = random.sample(self.grammar['<noun>'], 1)[0]
        # si le mot choisi "original_$", c'est qu'on choisit le nom d'origine
        if newValue == "original_$":
            # on le signale
            checkOriginNoun = "!original_noun!"
            # on garde en mémoire le nom original
            noun = self.noun
        # si c'est un synonyme
        elif newValue != "original_$":
            # on le signale
            checkOriginNoun = "!synonym_noun!"
            # on garde le mot choisi précédemment
            noun = newValue

        randomNoun = (noun, checkOriginNoun)

        return randomNoun


    # choisir aléatoirement un adverbe de fin de phrase
    # def randomAdverb(self):

    #     randomTimeAdverb = ()
    #     newValue = random.sample(self.grammar['<adverb_time>'], 1)[0]
    #     # si le mot choisi "original_$", c'est qu'on choisit le nom d'origine
    #     if newValue == "original_$":
    #         # on le signale
    #         checkOriginTimeAdv = "!original_adverb!"
    #         # on garde en mémoire le nom original
    #         adverb = self.adverb
    #     # si c'est un synonyme
    #     elif newValue != "original_$":
    #         # on le signale
    #         checkOriginAdverb = "!synonym_adverb!"
    #         # on garde le mot choisi précédemment
    #         adverb = newValue

    #     randomAdverb = (adverb, checkOriginTimeAdv)

    #     return randomAdverb


    ## RECUPERER LE GENRE / NOMBRE D'UN MOT

    # interpréter les indications de genre/nombre de Glawi concaténées aux noms
    def genderNumberNoun(self, nounType, noun):

        if nounType == "original":
            genderNumber = re.search("gender=(\w+)\|number=(\w+)", noun)
            if genderNumber:
                #nounWithoutGenderNumber = "not_needed"
                gender = genderNumber.group(1)
                number = genderNumber.group(2)
            else:
                gender = ""
                number = ""

        elif nounType == "synonym":
            genderNumber = re.search("(\S+)_gender=(\w+)\|number=(\w+)", noun)

            if genderNumber:
                #nounWithoutGenderNumber = genderNumber.group(1)
                gender = genderNumber.group(2)
                number = genderNumber.group(3)
            else:
                gender = ""
                number = ""
  
        genderNumberNoun = (gender,number)

        return genderNumberNoun


    ## FLECHISSEMENT DES PARTIES DU DISCOURS

    # trouver les flexions des déterminants interrogatifs, déterminants, auxiliaires selon le genre/nombre du nom 
    def detInterroAndAuxiliaryInflections(self, genderNumberNoun):

        detAndAuxInflections = {"det": "", "detInterro": "", "auxiliary": ""}

        gender = genderNumberNoun[0]
        number = genderNumberNoun[1]

        try :
            if gender == "m" and number == "s":
                det = "le"
                detInterro = "quel"
                auxiliary = "est"
            elif gender == "f" and number == "s":
                det = "la"
                detInterro = "quelle"
                auxiliary = "est"
            elif gender == "m" and number == "p":
                det = "les"
                detInterro = "quels"
                auxiliary = "sont"
            elif gender == "f" and number == "p":
                det = "les"
                detInterro = "quelles"
                auxiliary = "sont"
            elif gender == "m" and number == "sp" :
                det = "le"
                detInterro = "quel"
                auxiliary = "est"
            elif gender == "f" and number == "sp" :
                det = "la"
                detInterro = "quelle"
                auxiliary = "est"
            elif gender == "" and number == "":
                det = "le/la/les"
                detInterro = "quel/le/s"
                auxiliary = "est/sont"

            detAndAuxInflections = {"det": det, "detInterro": detInterro, "auxiliary": auxiliary}

        except UnboundLocalError :
            detAndAuxInflections = {"det": "le/la/les", "detInterro": "quel/le/s", "auxiliary": "est/sont"}


        return detAndAuxInflections


    # fléchir l'adjectif selon le nom
    def adjInflectionWithNoun(self, checkOriginAdj, chosenAdjective, genderNumberNoun):

        genderNoun = genderNumberNoun[0]
        numberNoun = genderNumberNoun[1]

        adjective = ""
        # si l'adjectif choisi est l'adjectif d'origine
        if checkOriginAdj == "!original_adjective!":
            # fléchir l'adjectif selon le nom (cas de l'adjectif original --> on prend l'adjectif lemmatisé précedemment)
            adjectiveLemma = self.getGlawiInputWordLemma(self.adjective, "adjectif")

            # si on a pu récupérer le lemme de l'adjectif
            if adjectiveLemma != "":

                try:
                    glawiObjectAdjective = self.dico[adjectiveLemma + "_adjectif"]
                    glawiObjectGenderNumber = "Afp" + genderNoun + numberNoun
                
                    adjective = glawiObjectAdjective['inflections'][glawiObjectGenderNumber]
                except KeyError:
                    adjective = adjectiveLemma

            # si on n'a pas pu récupérer le lemme de l'adjectif
            else:
                # soit c'est parce qu'il est déjà lemmatisé
                glawiObjectAdjective = self.dico[self.adjective + "_adjectif"]
                #print(glawiObjectAdjective)
                glawiObjectGenderNumber = "Afp" + genderNoun + numberNoun
                # soit parce qu'il n'est pas présent dans le dictionnaire
                try:
                    adjective = glawiObjectAdjective['inflections'][glawiObjectGenderNumber]
                except KeyError:
                    adjective = self.adjective
          
        # si l'adjectif choisi est un synonyme
        elif checkOriginAdj == "!synonym_adjective!":

            try:
                # le chercher dans Glawi
                glawiObjectAdjective = self.dico[chosenAdjective + "_adjectif"]
                # récupérer le code du genre et nombre voulu pour le fléchissement
                glawiObjectGenderNumber = "Afp" + genderNoun + numberNoun
            
                adjective = glawiObjectAdjective['inflections'][glawiObjectGenderNumber]

            except KeyError:
                adjective = chosenAdjective
   
        return adjective


    # fléchir le verbe selon un pronom et un temps donné
    def verbInflectionWithPronoun(self, verb, pronoun, tense):

        # définir le code du temps voulu dans Glawi
        if tense == "subj":
            glawiTense = "sp"
        elif tense == "impe":
            glawiTense = "mp"

        # définir le code du pronom dans Glawi
        if pronoun == "tu":
            glawiPronoun = "2s"
        elif pronoun == "vous":
            glawiPronoun = "2p"

        try :
            glawiObjectVerb = self.dico[verb + "_verbe"]
            glawiObjectInflection = "Vm" + glawiTense + glawiPronoun + "-"
            inflectedVerb = glawiObjectVerb['inflections'][glawiObjectInflection]

        except KeyError :
            inflectedVerb = verb

        # si un impératif est demandé, signaler qu'on ne veut pas de pronom
        if tense == "impe":
            pronoun = "x"
        else:
            pronoun = pronoun

        pronounVerb = (pronoun, inflectedVerb)

        return pronounVerb


    ## RECUPERER DES SYNONYMES DE PART OF SPEECH NON PREVUS DANS LES REGLES

    # récupérer toutes les entités présentes dans un ensemble de syntagmes prépositionnels
    def getAllEntitesInPrepSynt(self,prepSynt) :

        entitiesList = []
      
        for word in prepSynt :
            searchAnnot = re.search('\[(.+?)\]\((.+?)\)', word)
            if searchAnnot :
                annot = searchAnnot.group(2)
                entitiesList.append(annot)

        return entitiesList


    def filterPrepoSyntSynonyms(self, prepoSyntDic) :

        originalPrepSynt = []
        # liste qui contiendra uniquement les SP ayant les mêmes entités annotées que la phrase d'origine
        newPrepSyntSynonyms = []
        # rassembler tous les syntagmes prépositionnels de la phrase d'entrée dans un même tuple
        for index, ps in self.prepoSyntagm.items() :
            for p in ps :
                originalPrepSynt.append(p)
        originalPrepSynt = tuple(originalPrepSynt)

        originalPrepoSyntEntities = self.getAllEntitesInPrepSynt(originalPrepSynt)
        
        for sp in prepoSyntDic :
            synonymPrepoSyntEntities = self.getAllEntitesInPrepSynt(sp)
            if originalPrepoSyntEntities == synonymPrepoSyntEntities :
                newPrepSyntSynonyms.append(sp)

        return newPrepSyntSynonyms



    # récupérer les synonymes des syntagmes prépositionnels dans le fichier d'entrée
    def getSynonymPrepoSynt(self) :

        prepoSyntagm = ""
        joinedPrepSynt = ()
        originalPrepSyntString = ""
        originalPrepSyntLen = len(self.prepoSyntagm)
        prepSyntSynonymLen = len(self.prepSyntSynonyms)

        # vérifier s'il existe des syntagmes prépositionnels dans la phrase d'entrée
        if originalPrepSyntLen > 0 :
            # vérifier que la liste des synonymes de SP soit disponible
            if prepSyntSynonymLen > 0 :
                for key, value in self.prepSyntSynonyms.items() :

                    # chercher des SP ayant le même nombre de mots que le SP d'origine
                    try :
                        if key == originalPrepSyntLen :
                            # filtrer les SP ayant le même nombre de mots
                            # ne garder que ceux ayant les mêmes entités annotées que dans la phrase d'entrée
                            dicoSynonyms = self.filterPrepoSyntSynonyms(value)
                            # choisir un ensemble de SP parmi ceux-là
                            chosenPrepSynt = random.choice(list(dicoSynonyms))
                            #chosenPrepSynt = random.choice(list(value))

                            # transformer le SP choisi en string
                            for word in chosenPrepSynt :
                                prepoSyntagm = prepoSyntagm + " " + word
                        # appliquer l'annotation
                        #prepoSyntagm = self.posAnnotations.applyPrepSyntAnnotations(chosenPrepSynt)

                    # s'il n'y a pas d'ensemble de SP synonyme compatible, renvoyer le syntagme prépositionnel d'origine
                    except UnboundLocalError :

                        # préparer le synt prépo d'origine pour l'annotation en concaténant tous les SP
                        for number, prepSyntElements in self.prepoSyntagm.items() :
                            for el in prepSyntElements :
                                originalPrepSyntString = originalPrepSyntString + " " + el

                        prepoSyntagm = originalPrepSyntString

            # s'il n'y pas de synonymes disponibles, renvoyer le syntagme prépositionnel d'origine
            else : 
                # préparer le synt prépo d'origine pour l'annotation
                for number, prepSyntElements in self.prepoSyntagm.items() :
                    for el in prepSyntElements :
                        #joinedPrepSynt = joinedPrepSynt + prepSyntElements
                        originalPrepSyntString = originalPrepSyntString + " " + el

                prepoSyntagm = originalPrepSyntString

        # s'il n'existe pas de syntagme prépositionnel dans la phrase d'entrée, renvoyer une string vide
        else:
            prepoSyntagm = ""

        return prepoSyntagm


    # def getSynonymPrepoSynt(self) :

    #     print(self.prepSyntSynonyms)
    #     prepoSyntagm = ""
    #     joinedPrepSynt = ()
    #     originalPrepSyntString = ""
    #     originalPrepSyntLen = len(self.prepoSyntagm)
    #     prepSyntSynonymLen = len(self.prepSyntSynonyms)

    #     # vérifier s'il existe des syntagmes prépositionnels dans la phrase d'entrée
    #     if originalPrepSyntLen > 0 :
    #         # vérifier que la liste des synonymes de SP soit disponible
    #         if prepSyntSynonymLen > 0 :
    #             for key, value in self.prepSyntSynonyms.items() :

    #                 # chercher des SP ayant le même nombre de mots que le SP d'origine
    #                 try :
    #                     if key == originalPrepSyntLen :

    #                         # choisir un ensemble de SP parmi ceux-là
    #                         #chosenPrepSynt = random.choice(list(value))
    #                         prepoSyntagm = random.choice(list(value))
            
    #                     # appliquer l'annotation
    #                     #prepoSyntagm = self.posAnnotations.applyPrepSyntAnnotations(chosenPrepSynt)
    #                     for number, prepSyntElements in prepoSyntagm.items() :
    #                         joinedPrepSynt = joinedPrepSynt + prepSyntElements
    #                     prepoSyntagm = joinedPrepSynt

    #                 # s'il n'y a pas d'ensemble de SP synonyme compatible, renvoyer le syntagme prépositionnel d'origine
    #                 except UnboundLocalError :

    #                     # préparer le synt prépo d'origine pour l'annotation en concaténant tous les SP
    #                     for number, prepSyntElements in self.prepoSyntagm.items() :
    #                         for el in prepSyntElements :
    #                             originalPrepSyntString = originalPrepSyntString + " " + el

    #                     prepoSyntagm = originalPrepSyntString

    #         # s'il n'y pas de synonymes disponibles, renvoyer le syntagme prépositionnel d'origine
    #         else : 
    #             # préparer le synt prépo d'origine pour l'annotation
    #             for number, prepSyntElements in self.prepoSyntagm.items() :
    #                 for el in prepSyntElements :
    #                     #joinedPrepSynt = joinedPrepSynt + prepSyntElements
    #                     originalPrepSyntString = originalPrepSyntString + " " + el

    #             prepoSyntagm = originalPrepSyntString

    #     # s'il n'existe pas de syntagme prépositionnel dans la phrase d'entrée, renvoyer une string vide
    #     else:
    #         prepoSyntagm = ""

    #     return prepoSyntagm



    ### Ajout des éléments qui composent le syntagme nominal (nom, adjectif)

    ## AJOUT DE L'ADJECTIF 

    # insérer l'adjectif dans le syntagme nominal
    def adjectiveInNominalSyntagm(self, result, word, genderNumberNoun, outPutNoun):

        # s'il y a un adjectif dans la phrase originale
        if self.adjective != "":
            # on choisit un adjectif dans la liste des ressources
            randomAdjective = self.randomAdjective()
            chosenAdjective = randomAdjective[0]
            checkAdjOrigin = randomAdjective[1]

            # fléchir l'adjectif selon le nom choisi précédemment
            inflectedAdjective = self.adjInflectionWithNoun(checkAdjOrigin, chosenAdjective, genderNumberNoun)

            # appliquer les annotations de l'adjectif d'origine
            outPutAdj = self.posAnnotations.applyWordAnnotations(inflectedAdjective, "adjective")

            # varier les entités qui composent les syntagmes prépositionnaux
            outPutPrepoSyntagm = self.getSynonymPrepoSynt()

            # annoter les appositions du nom
            outPutFolloNomSynt = self.posAnnotations.applyFollowingNomSyntAnnotations()

            # vérifier s'il y avait un adverbe à la fin de la phrase et former le syntagme final
            if self.adverb != "" :
                # annoter l'adverbe
                outPutAdverb = self.posAnnotations.applyWordAnnotations(self.adverb, "adverb")
                newValue = outPutNoun + " " + outPutAdj + " " + outPutFolloNomSynt + " " + outPutPrepoSyntagm + " " + outPutAdverb
            else :
                newValue = outPutNoun + " " + outPutAdj + " " + outPutFolloNomSynt + " " + outPutPrepoSyntagm
            
            result = result.replace(word, newValue, 1)

        # s'il n'y a pas d'adjectif on concatène directement le nom avec le syntagme prépositionnel
        elif self.adjective == "":

            outPutPrepoSyntagm = self.getSynonymPrepoSynt()

            outPutFolloNomSynt = self.posAnnotations.applyFollowingNomSyntAnnotations()

            if self.adverb != "" :
                outPutAdverb = self.posAnnotations.applyWordAnnotations(self.adverb, "adverb")
                newValue = outPutNoun + " " + outPutFolloNomSynt + " " + outPutPrepoSyntagm + " " + outPutAdverb
            else :
                newValue = outPutNoun + " " + outPutFolloNomSynt + " " + outPutPrepoSyntagm
            result = result.replace(word, newValue, 1)

        return result


    ## AJOUT DE L'ADVERBE

    # ajouter l'adverbe à la phrase
    def adverbInSentence(self, result, word) :

        # s'il existe un adverbe de fin de phrase dans la phrase d'entrée
        if self.adverb != "" :
            # on choisit un adjectif dans la liste des ressources
            randomAdverb = self.randomAdverb()
            chosenAdverb = randomAdverb[0]
            checkAdvOrigin = randomAdverb[1]

            if checkAdvOrigin == "!original_adverb!" :

                outPutAdverb = self.adverb

            elif checkAdvOrigin == "!synonym_adverb!" :

                outPutAdverb = chosenAdverb

        
        result = result.replace(word, newValue, 1)

        return result



    ## AJOUT DU NOM (+ ADJECTIF EVENTUEL + SYNTAGMES PREPOSITIONNAUX EVENTUELS)

    # traitement spécifique si le nom original est choisi parmi la liste des noms
    def originalNounChosenInList(self, result, word):

        # récupérer le genre et nombre du nom indiqués de l'objet Glawi
        inputGlawiNounGenderNumber = self.getGlawiInputWordGenderNumber(self.noun, "nom")
        # traiter les ratés et absences de résultats des genre et nombre de l'objet Glawi
        genderNumberNoun = self.genderNumberNoun("original", inputGlawiNounGenderNumber)

        # appliquer les annotations de la phrase d'origine aux nouvelles phrases
        outPutNoun = self.posAnnotations.applyWordAnnotations(self.noun, "noun") #(chosenNoun, "noun")

        # vérifier si le nom est un nom commun ou un nom propre
        checkIfProperNoun = self.checkProperNoun(outPutNoun)

        # si le nom est un nom commun 
        if checkIfProperNoun == False :

            # déterminants et verbes d'état fléchis selon le genre/nombre du nom d'origine
            detInterroAndAuxInflections = self.detInterroAndAuxiliaryInflections(genderNumberNoun)

            # ajouter l'adjectif s'il y en avait un dans la phrase d'entrée et renvoyer le résultat final du syntagme nominal
            result = self.adjectiveInNominalSyntagm(result, word, genderNumberNoun, outPutNoun)

            # renvoyer le SN final + les déterminants ... fléchis
            nominalSyntInformations = (detInterroAndAuxInflections, result)

        elif checkIfProperNoun == True :

            result = self.adjectiveInNominalSyntagm(result, word, genderNumberNoun, outPutNoun)

            nominalSyntInformations = ({"det": "PN", "detInterro": "PN", "auxiliary": "PN"}, result)


        return nominalSyntInformations


    # traitement spécifique si un synonyme est choisi dans la liste des noms
    def synonymNounChosenInList(self, result, word, chosenNoun):

        # traiter les ratés et absences de résultats des genre et nombre de l'objet Glawi
        genderNumberNoun = self.genderNumberNoun("synonym", chosenNoun)

        # appliquer les annotations de la phrase d'origine aux nouvelles phrases
        # récupérer le nom synonyme sans ses indications de genre/nombre
        getNounWithoutGenNum = re.search("(\S+)_gender=(\S+)?\|number=(\S+)?", chosenNoun) 
        chosenNoun = getNounWithoutGenNum.group(1) 

        # appliquer les bonnes annotations
        outPutNoun = self.posAnnotations.applyWordAnnotations(chosenNoun, "noun")

        # vérifier si le nom est un nom commun ou un nom propre
        checkIfProperNoun = self.checkProperNoun(outPutNoun)

        # si le nom est un nom commun 
        if checkIfProperNoun == False :

            # déterminants et verbes d'état fléchis selon le genre/nombre du nom choisi
            detInterroAndAuxInflections = self.detInterroAndAuxiliaryInflections(genderNumberNoun)

            # ajouter l'adjectif et renvoyer le résultat final
            result = self.adjectiveInNominalSyntagm(result, word, genderNumberNoun, outPutNoun)

            # renvoyer le SN final + les déterminants ... fléchis
            nominalSyntInformations = (detInterroAndAuxInflections, result)

        # sinon si le nom est un nom propre
        elif checkIfProperNoun == True :

            result = self.adjectiveInNominalSyntagm(result, word, genderNumberNoun, outPutNoun)

            # signaler que le nom est un nom propre
            nominalSyntInformations = ({"det": "PN", "detInterro": "PN", "auxiliary": "PN"}, result)


        return nominalSyntInformations


    # vérifier si le nom est un nom propre
    def checkProperNoun(self, outPutNoun) :

        properNoun = False
        # vérifier si le nom a été annoté "people" dans Tock
        checkProperNoun = re.search('\[(.+?)\]\((people)\)', outPutNoun)
        if checkProperNoun :
            properNoun = True

        return properNoun

    
    ## REMPLACER LES ELEMENTS DE LA REGLE

    # remplacer <noun> dans la règle
    def replaceNounInRules(self, result, word):

        # traiter la balise <noun>
        # si la phrase d'entrée comporte bien un nom
        if self.noun != "":
            # choix d'un nom aléatoire (chosenNoun) + signale si le nom choisi est l'original ou un synonyme (checkOrigin)
            randomNoun = self.randomNoun()
            chosenNoun = randomNoun[0]
            checkNounOrigin = randomNoun[1]

            # si le nom d'origine est choisi
            if checkNounOrigin == "!original_noun!":

                nominalSyntInformations = self.originalNounChosenInList(result, word)
                detInterroAndAuxInflections = nominalSyntInformations[0]
                result = nominalSyntInformations[1]
                
            # si un synonyme du nom est choisi
            elif checkNounOrigin == "!synonym_noun!":
                
                nominalSyntInformations = self.synonymNounChosenInList(result, word, chosenNoun)
                detInterroAndAuxInflections = nominalSyntInformations[0]
                result = nominalSyntInformations[1]

            nounReplacement = (result, checkNounOrigin, detInterroAndAuxInflections)

        # s'il n'y a pas de nom dans la phrase d'entrée, on garde le syntagme prépositionnel tout seul
        else:
            detInterroAndAuxInflections = {"det": "", "detInterro": "", "auxiliary": ""}
            newValue = self.getSynonymPrepoSynt()
            result = result.replace(word, newValue, 1) 
            nounReplacement = (result, "", detInterroAndAuxInflections)

   
        return nounReplacement 


    # remplacer <interro_info_etat> dans la règle
    def replaceInterroDetInRules(self, result, word, detInterro):
        if self.noun != "":
            newValue = detInterro
            result = result.replace(word, newValue, 1)
        else:
            result = result.replace(word,"", 1)

        return result


    # remplacer <verb_etat> dans la règle
    def replaceAuxiliaryInRules(self, result, word, auxiliary):

        newValue = auxiliary 
        result = result.replace(word, newValue, 1)

        return result


    # remplacer <det> dans la règle
    def replaceDetInRules(self, result, word, det, checkNounOrigin):
        if self.noun != "": 
           
            # si le nom est un nom propre, omettre le déterminant
            if det == "PN":
                det = ""

            # s'il s'agit du nom en entrée
            if checkNounOrigin == "!original_noun!":
                # s'il n'y avait pas de déterminant en entrée
                if self.determinant == "":
                    # récupérer le déterminant fléchi précédemment
                    newValue = det
                    result = result.replace(word, newValue, 1)
                # s'il y en avait un, récupérer le déterminant en entrée
                else:
                    newValue = self.determinant #"le/la/les_" + essaiOrigin # 
                    result = result.replace(word, newValue, 1)
            # si le nom est un synonyme
            else:
                # récupérer le déterminant fléchi dans la précédente étape
                newValue = det
                result = result.replace(word, newValue, 1)
                # si le nom n'existe pas
        elif self.noun == "":
            # on ne met rien à la place du déterminant
            result = result.replace(word, "", 1)

        return result


    # remplacer <verb> dans la règle
    def replaceInfinitiveVerbInRule(self, result, word):

        chosenVerb = random.sample(self.grammar[word], 1)[0]
        # si on choisit "original_$"
        if chosenVerb == "original_$":
            # le verbe choisi est l'original, récupération de son lemme
            chosenVerb = self.getGlawiInputWordLemma(self.verb, "verbe")
            # ajout des annotations d'origine
            outPutVerb = self.posAnnotations.applyWordAnnotations(chosenVerb, "verb")
            result = result.replace(word, outPutVerb, 1)
        # si le verbe choisi est un synonyme
        else:
            # ajout des annotations
            outPutVerb = self.posAnnotations.applyWordAnnotations(chosenVerb, "verb")
            result = result.replace(word, outPutVerb, 1)

        return result


    # remplacer <verb_tense_?> dans la règle
    def replaceInflectedVerbInRule(self,result, word):

        # générer un pronom aléatoire
        # pronouns = ["tu","vous"]
        # pronoun = random.choice(pronouns)
        pronoun = "tu"

        # récupérer le temps voulu
        tense = word[-5:][:-1] 
        # choisir un verbe
        chosenVerb = random.sample(self.grammar['<verb>'], 1)[0]

        # verbe original
        if chosenVerb == "original_$":
            # récupérer le lemme du verbe d'entrée
            verbLemma = self.getGlawiInputWordLemma(self.verb, "verbe")
            # conjuguer le verbe choisi au temps voulu
            pronounVerb = self.verbInflectionWithPronoun(verbLemma, "tu", tense)

            pronoun = pronounVerb[0]
            chosenVerb = pronounVerb[1]

            # appliquer l'annotation du verbe d'origine au nouveau verbe
            outPutVerb = self.posAnnotations.applyWordAnnotations(chosenVerb, "verb") 

            # si le verbe est à l'impératif, on omet le pronom
            if pronoun == "x":
                result = result.replace(word, outPutVerb, 1)
            # s'il est à un autre temps, on le garde
            else:
                result = result.replace(word, pronoun + " " + outPutVerb, 1)
                    

        # verbe synonyme
        else:
            pronounVerb = self.verbInflectionWithPronoun(chosenVerb, pronoun, tense)
            pronoun = pronounVerb[0]
            chosenVerb = pronounVerb[1]

            outPutVerb = self.posAnnotations.applyWordAnnotations(chosenVerb, "verb")

            # si le verbe est à l'impératif, on omet le pronom
            if pronoun == "x":
                result = result.replace(word, outPutVerb, 1)
            # s'il est à un autre temps, on le garde
            else:
                result = result.replace(word, pronoun + " " + outPutVerb, 1)

        return result


    # remplacer les balises de la grammaire par les parties du discours correspondantes
    def replaceRuleElementByPos(self, ruleContent):

        result = ruleContent
        words = ruleContent.split()
        checkNounOrigin = ""
        detAndAuxInflections = {}

        # parcourir les éléments de la règle
        # l'élément <noun> est traité en priorité, c'est de lui que dépend le fléchissement du reste des éléments
        for word in words:
            if word == "<noun>":
                nounReplacement = self.replaceNounInRules(result, word)
                result = nounReplacement[0]
                checkNounOrigin = nounReplacement[1]
                detAndAuxInflections = nounReplacement[2]

        # pour chaque autre balise dans la règle, traitement spécifique
        for word in words:
          
            # fléchir le déterminant interrogatif selon le genre / nombre du nom (quel(les))
            if word == "<interro_determinant>":
                detInterro = detAndAuxInflections["detInterro"]
                result = self.replaceInterroDetInRules(result, word, detInterro)

            # le/la/les
            elif word == "<det>":
                det = detAndAuxInflections["det"]
                result = self.replaceDetInRules(result, word, det, checkNounOrigin)

            # si c'est un élement <verb> on attend un verbe à l'infinitif
            elif word == "<verb>":
                result = self.replaceInfinitiveVerbInRule(result, word)
            # est/sont
            elif word == "<verb_auxiliary>":
                auxiliary = detAndAuxInflections["auxiliary"]
                result = self.replaceAuxiliaryInRules(result, word, auxiliary)

            # conjuguer le verbe selon le pronom choisi précédemment et au temps indiqué dans la règle
            elif word[:11] == "<verb_tense":
                result = self.replaceInflectedVerbInRule(result, word)
                
            # pour les éléments de règle restants: les remplacer par un élément random de leur liste
            elif word in self.grammar and re.match(r'<\w+>',word):
                newValue = random.sample(self.grammar[word], 1)[0]
                result = result.replace(word, newValue, 1)

        return result
    

    # générer la nouvelle phrase
    def generateSimilarExpre(self, startRule):

        if len(self.grammar) == 0:
            raise Exception('Empty grammar.')
        start = self.grammar.get(startRule)
        if start == None:
            raise Exception('Start rule not in grammar.')
        generatedString = startRule 
        #print(generatedString)
        while generatedString.find('<') != -1:
            generatedString = self.replaceRuleElementByPos(generatedString)

        # régler les liaisons des voyelles
        generatedString = self.vowelsInGenString(generatedString)
        
        return generatedString.lstrip(' ')


    # régler les liaisons dues aux voyelles (ex: de le -> du , )
    def vowelsInGenString(self,generatedString):

        # remplacer les doubles espaces possibles
        generatedString = re.sub(' +', ' ', generatedString)

        # traiter les "de le" laissés par coreNLP et les remplacer par "du"
        deLe = re.compile('(^|\s)de le\s')
        generatedString = deLe.sub('\\1du ', generatedString)

        # "de les"
        deLes = re.compile('(^|\s)de les')
        generatedString = deLes.sub('\\1des ', generatedString)

        # "à le"
        aLe = re.compile('(^|\s)à le')
        generatedString = aLe.sub('\\1au', generatedString)

        # "à les"
        aLes = re.compile('(^|\s)à les')
        generatedString = aLes.sub('\\1aux', generatedString)

        # remplacer les de + voyelle en d'
        deVowel = re.compile('(^|\s)(de) (\[?[hâaeéèêiîïouy])')
        generatedString = deVowel.sub('\\1d\'\\3', generatedString)

        # remplacer les la + voyelle par l'
        detVowel = re.compile('(^|\s)(l[ea]) (\[?[hâaeéèêiîïouy])') 
        generatedString = detVowel.sub('\\1l\'\\3', generatedString)

        l = re.compile('l\' ')
        generatedString = l.sub('l\'', generatedString)

        return generatedString

