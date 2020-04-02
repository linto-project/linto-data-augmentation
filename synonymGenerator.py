# -*- coding: utf-8 -*-
import re

######## GENERATEUR DE SYNONYMES

class synonymGenerator:

	#def __init__(self, glawiObject, filepath, gramCatAnnotation):
		
	def __init__(self, glawi, gramCatAnnotation, intentSentPos, intent):

		# objet Glawi
		self.glawi = glawi
		
		# les part of speech de la phrase et leur entités annotées
		# ex: {'noun': 'light', 'adjective': 'type_cultural'}
		self.gramCatAnnotation = gramCatAnnotation

		# part of speech de toutes les phrases du fichier de commandes
		#self.partsOfSpeech = {"- [allume](action_on) la [lumière](light)" : {"verb": "allume", "noun": "lumière"... }}
		self.intentSentPos = intentSentPos

		# l'intention actuellement traitée
		self.intent = intent


	# récupérer toutes les instances d'entités dans l'intention actuelle
	def getAllAnnotationsInIntent(self) :

		# récupérer les phrases de l'intention donnée
		intentSent = self.intentSentPos[self.intent]
		annotationsList = {}

		for sentence, pos in intentSent.items() :
			searchAnnotations = re.findall('(\[(.+?)\]\((.+?)\))', sentence)
			for annot in searchAnnotations :
					if annot[2] not in annotationsList:
						annotationsList[annot[2]] = [annot[1].lower()]
					else:
						if annot[1].lower() not in annotationsList[annot[2]] : 
							annotationsList[annot[2]].append(annot[1].lower())

		return annotationsList



	# récupérer les listes d'instances d'entités à injecter dans les ressources verbe, nom et adjectif
	# {'verbSynonyms' : ['allumer', 'déclencher'...], 'nounSynonyms' : ['chronomètre'...]}
	def getAnnotationsSynonyms(self):

		# synonymes utiles
		posSynonyms = {}

		# récupérer les entités correspondant à chaque catégorie grammaticale
		# gramCatAnnotation = {'verb' : 'action_on', 'noun' : 'recording' ...}
		verbAnnot = self.gramCatAnnotation['verb']
		nounAnnot = self.gramCatAnnotation['noun']
		adjAnnot = self.gramCatAnnotation['adjective']

		
		# récupérer toutes les entités et leurs instances dans le document
		# 'action_on' : ['allumer', 'déclencher'], langue': ['anglais', 'finlandais'], 'objet': ['plante'] ... 
		allAnnotationsInDoc = self.getAllAnnotationsInIntent() #self.getAllAnnotationsInDoc()
		
		# récupérer la liste des instances de l'entité utilisée pour un part of speech
		# ex : le verbe de la phrase d'entrée est annoté 'action_on'
		# on récupère toutes les instances de l'entité 'action_on' pour les injecter plus tard dans les ressources <verb>
		try:
			verbSynonyms = allAnnotationsInDoc[verbAnnot]
		except KeyError:
			verbSynonyms = ""

		try:
			nounSynonyms = allAnnotationsInDoc[nounAnnot]
		except KeyError:
			nounSynonyms = ""

		try:
			adjSynonyms = allAnnotationsInDoc[adjAnnot]
		except KeyError:
			adjSynonyms = ""

		posSynonyms["verbSynonyms"] = verbSynonyms
		posSynonyms["nounSynonyms"] = nounSynonyms
		posSynonyms["adjSynonyms"] = adjSynonyms
		#print(posSynonyms)


		return posSynonyms


	# récupérer les part of speech ayant des entités associées dans le fichier des commandes
	# ex: [allumer](action_on)
	def getAnnotedPosSynonyms(self):

		synonymLists = self.getAnnotationsSynonyms()
	
		annotedPosSynonymsList = {'verbSynonyms':[], 'nounSynonyms':[], 'adjSynonyms':[]}
		for key,value in synonymLists.items():
			if key == "verbSynonyms":
				gramCat = "verbe"
			elif key == "nounSynonyms":
				gramCat = "nom"
			elif key == "adjSynonyms":
				gramCat = "adjectif"

			# récupérer le lemme des synonymes
			for v in value :
				wordLemma = self.glawi.getWordLemma(v, gramCat)
				# on ne prend pas de doublon
				if wordLemma not in annotedPosSynonymsList[key] :
					annotedPosSynonymsList[key].append(wordLemma)
		
		return annotedPosSynonymsList



	# récupérer les parts of speech n'ayant pas reçu d'entités associées
	# pour plus de précision, on ne garde que les parts of speech de la même intention comme synonymes
	def getNonAnnotedPosSynonyms(self, intent, intentSentPos):


		# récupérer les phrases de l'intention donnée
		intentSentences = intentSentPos[intent]
		# récupérer les pos de chaque phrase
		nonAnnotedPosSynonymsList = {'verbSynonyms': [], 'nounSynonyms': [], 'adjSynonyms': []}
		for sentence, partsOfSpeech in intentSentences.items() :
			for pos, posValue in partsOfSpeech.items() :
				
				if pos == 'verb':
					if posValue != '' and posValue not in nonAnnotedPosSynonymsList['verbSynonyms']:
						# récupérer le lemme des synonymes
						gramCat = "verbe"
						wordLemma = self.glawi.getWordLemma(posValue, gramCat)
						if wordLemma not in nonAnnotedPosSynonymsList['verbSynonyms'] :
							nonAnnotedPosSynonymsList['verbSynonyms'].append(wordLemma)

				if pos == 'noun':
					if posValue != '' and posValue not in nonAnnotedPosSynonymsList['nounSynonyms']:
					
						nonAnnotedPosSynonymsList['nounSynonyms'].append(posValue)

				if pos == 'adjective':
					if posValue != '' and posValue not in nonAnnotedPosSynonymsList['adjSynonyms']:
						gramCat = "adjectif"
						wordLemma = self.glawi.getWordLemma(posValue, gramCat)
						if wordLemma not in nonAnnotedPosSynonymsList['adjSynonyms'] :
							nonAnnotedPosSynonymsList['adjSynonyms'].append(wordLemma)

		return nonAnnotedPosSynonymsList



	# fusionner les listes de synonymes récupérées via les annotations et via les part of speech non annotés
	def mergeSynonymLists(self, annotedPosSynonymsList, nonAnnotedPosSynonymsList):

		# liste des instances d'entités dans l'intention
		allAnnotationsInIntent = self.getAllAnnotationsInIntent()

		# listes finales
		synoList = []
		synonymsList = {'verbSynonyms': [], 'nounSynonyms': [], 'adjSynonyms': []}
		mergedList = []

		for key,value in annotedPosSynonymsList.items() :
			for k,v in nonAnnotedPosSynonymsList.items() :
				if key == k and len(value) != 0:
					synonymsList[key] = value
				elif key == k and len(value) == 0 :
					synonymsList[key] = v
					#synonymsList[key] = list(set(value + v))

		return synonymsList



	# récupérer les synonymes de syntagmes prépositionnels
	def getPrepoSyntagmSynonyms(self, intent) :

		prepoSyntagmSynonyms = {}
		prepSyntSynonym = ()

		# phrase et part of speech de l'intention donnée
		intentSentences = self.intentSentPos[intent]

		# pour chaque phrase et parties du discours dans l'intention donnée
		for sentence, pos in intentSentences.items() :
			# pour chaque partie du discours et sa valeur correspondante
			for posName, posValue in pos.items() :
				# récupérer le nombre de syntagmes prépositionnels dans la phrase {1: (de, pollution) 2: (à Toulouse)} --> 2 SP
				if posName == "prepoSyntagm" :
					prepSyntLen = len(posValue)

					for number,prepSyntWords in posValue.items() :
						# rassembler ces SP en un seul tuple (de, pollution, à, Toulouse)
						prepSyntSynonym = prepSyntSynonym + prepSyntWords

					# rassembler les tuples de syntagmes prépositionnaux ayant la même longueur dans les mêmes listes
					# {2: [('de', 'pollution', 'à', 'Paris'), ('de', 'pollution', 'à', 'Toulouse')], 1: [('de', 'pollution')]}
					if prepSyntLen not in prepoSyntagmSynonyms :
						prepoSyntagmSynonyms[prepSyntLen] = []
						prepoSyntagmSynonyms[prepSyntLen] = [prepSyntSynonym]
						prepSyntSynonym = ()
					else :
						prepoSyntagmSynonyms[prepSyntLen].append(prepSyntSynonym) 
						prepSyntSynonym = ()

		
		return prepoSyntagmSynonyms



						





