# -*- coding: utf-8 -*-

import re


class MarkDownContent:

    def __init__(self, markdown):
        self.markdown = markdown

    # récupérer toutes les intentions et leurs phrases correspondantes
    # dictionnaire -> {'control': ['- [allume](action_on) la [lumière](light)', '- [allumer](action_on) la [lumière](light)']}
    def extractIntentsAndSentences(self):

        intentsSentences = {}
        sentences = []
        intent = ""

        for line in self.markdown.split('\n'):
            searchIntent = re.search('## intent:(\w+)', line)
            if searchIntent:
                # checkNewIntent = False
                if intent != "":
                    intentsSentences[intent] = sentences
                intent = searchIntent.group(1)
                sentences = []

            else:
                l = line.rstrip('\n')
                if l != '':
                    sentences.append(l)


            if len(sentences) != 0:
                intentsSentences[intent] = sentences

        return intentsSentences

    # ajouter les part of speech à chaque phrase de chaque intention
    # { videoconf : {"démarrer la conférence" :
    #					{"verb": "démarrer",
    #					 "noun": "conférence"
    #					  ...
    #					}
    #				"allume la caméra" :
    #					{"verb": "allume",
    #					 "noun": "caméra"
    #					  ...
    #					}
    #				}
    # }

    def getIntentSentPos(self, nlpEngine):

        # récupérer le dictionnaire des intentions accompagnées de leurs phrases
        intentsSentences = self.extractIntentsAndSentences()
        sentPos = {}
        intentSentPos = {}

        # pour chaque intention et liste des phrases
        for key, value in intentsSentences.items():
            # pour chaque phrase
            for v in value:
                nlpEngine.analyseSentenceCoreNLP(v)
                # récupérer tous les part of speech de la phrase
                partsOfSpeech = nlpEngine.getAllPosInSentence()
                # ajouter les part of speech comme valeur de la phrase
                sentPos[v] = partsOfSpeech
            # ajouter ce nouveau dictionnaire aux intentions
            intentSentPos[key] = sentPos
            sentPos = {}

        return intentSentPos







