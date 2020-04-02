# -*- coding: utf-8 -*-
from NLPEngine import NLPEngine
import re

class loadSentencesFile:

	def __init__(self, filepath, nlpEngine):
		self.filepath = filepath
		self.nlpEngine = nlpEngine


	# récupérer toutes les intentions et leurs phrases correspondantes
	# dictionnaire -> {'control': ['- [allume](action_on) la [lumière](light)', '- [allumer](action_on) la [lumière](light)']}
	def getIntentsAndSentencesInFile(self):

		intentsSentences = {}
		sentences = []
		intent = ""
	
		with open(self.filepath, encoding="utf-8") as fp:

			line = fp.readline()
			while line:
				searchIntent = re.search('## intent:(\w+)', line)
				if searchIntent:
					#checkNewIntent = False
					if intent != "":
						intentsSentences[intent] = sentences
					intent = searchIntent.group(1)
					sentences = []

				else:
					l = line.rstrip('\n')
					if l != '':
						sentences.append(l)

				line = fp.readline()

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

	
	def getIntentSentPosInFile(self) :

		# récupérer le dictionnaire des intentions accompagnées de leurs phrases
		intentsSentences = self.getIntentsAndSentencesInFile()
		sentPos = {}
		intentSentPos = {}

		# pour chaque intention et liste des phrases
		for key,value in intentsSentences.items():
			# pour chaque phrase
			for v in value:
				self.nlpEngine.analyseSentenceCoreNLP(v)
				# récupérer tous les part of speech de la phrase
				partsOfSpeech = self.nlpEngine.getAllPosInSentence()
				# ajouter les part of speech comme valeur de la phrase
				sentPos[v] = partsOfSpeech
			# ajouter ce nouveau dictionnaire aux intentions
			intentSentPos[key] = sentPos
			sentPos = {}

		return intentSentPos





		

