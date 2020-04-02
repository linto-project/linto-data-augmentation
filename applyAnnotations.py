# -*- coding: utf-8 -*-
import re


## Récupérer les annotations de la commande d'entrée pour les appliquer aux commandes synonymes

class applyAnnotations:

	def __init__(self, sentence, sentenceElements):

		# part of speech récupérés précédemment
		self.verb = sentenceElements.getVerb()
		self.noun = sentenceElements.getNoun()
		self.adjective = sentenceElements.getAdjective()
		self.followingNomSynt = sentenceElements.getFollowingNominalSyntagms()
		self.prepoSyntagm = sentenceElements.getPrepoSyntagm()
		self.adverb = sentenceElements.getAdverb()


		# dictionnaire qui va contenir les part of speech de la nouvelle phrase avec leurs annotations
		# par défaut : les part of speech sans leurs annotations
		self.annotedPos = {}
		self.annotedPos["noun"] = (False, self.noun)
		self.annotedPos["adjective"] = (False, self.adjective)
		self.annotedPos["verb"] = (False, self.verb)
		self.annotedPos["followingNomSynt"] = (False, self.followingNomSynt)
		self.annotedPos["prepoSyntagm"] = (False, self.prepoSyntagm)
		self.annotedPos["adverb"] = (False, self.adverb)

		# chercher tous les mots annotés dans la phrase d'entrée
		regexAnnotWords = r'(\[(\S+?(?: \S+)*)\]\((\w+)\))'
		# liste des mots annotés
		annotedWords = re.findall(regexAnnotWords, sentence)

		# comparer les mots/expressions annotées avec les part of speech de coreNLP
		for l in annotedWords:
			# groupe capturant correspondant à la version du mot avec le markdown (ex: [jour](time) )
			annotedWord = l[0]

			# groupe capturant correspondant à la version du mot débarassée du markdown (ex: [jour](time) --> jour)
			nonAnnotedWord = l[1]
	
			# groupe capturant correspondant à l'annotation (ex: [jour](time) -> time)
			wordAnnotation = l[2]

			# vérifier si le nom a été annoté
			if nonAnnotedWord == self.noun:
                # sa version non annotée est remplacée par sa version annotée
				self.annotedPos["noun"] = (True, wordAnnotation)
            
            # vérifier si l'adjectif a été annoté
			if nonAnnotedWord == self.adjective:
				self.annotedPos["adjective"] = (True, wordAnnotation)


            # vérifier si le verbe a été annoté
			if self.verb != "":
				if nonAnnotedWord == self.verb:
					self.annotedPos["verb"] = (True, wordAnnotation)

			# vérifier si l'adverbe a été annoté
			if nonAnnotedWord == self.adverb:
				self.annotedPos["adverb"] = (True, wordAnnotation)

			
			# vérifier si les appositions ont été annotées
			if nonAnnotedWord in self.followingNomSynt :
				self.followingNomSynt = re.sub(nonAnnotedWord, annotedWord, self.followingNomSynt)
				self.annotedPos['followingNomSynt'] = (True, self.followingNomSynt)


	        # vérifier si un mot du syntagme prépositionnel a été annoté
	        # pour l'instant, traitement spécifique dû au fait que le syntagme prépositionnel est figé (pas d'utilisation de synonymes)
			for k,v in list(self.prepoSyntagm.items()):
				# les syntagmes prépositionnels sont sous la forme de tuples (de, le, jour) ou (à, Toulouse)
				# comparer les mots annotés avec le nom trouvé dans la phrase
				lenTuplePrepSyntagm = len(v)

				# chercher dans la liste des mots / expressions annotés
				for l in annotedWords:

					# si le syntagme a la forme (à, Toulouse)
					if lenTuplePrepSyntagm == 2:
	                    # on récupère "Toulouse"
						nounInTuple = v[1]
						# si "Toulouse" a déjà été trouvé grâce à coreNLP
						if nounInTuple == nonAnnotedWord:
							#print (annotedWord)
							convTuple = list(v)
							convTuple[1] = annotedWord
							self.prepoSyntagm[k] = tuple(convTuple)

	                       
					# si le syntagme a la forme (de, le, jour) ou (pour, 5, minutes)
					elif lenTuplePrepSyntagm == 3:
						# on récupère le nom -> "jour"
						firstNounInTuple = v[2]
						# on récupère éventuellement un autre nom ou chiffre -> "5" qui remplace le déterminant
						secondNounInTuple = v[1]
						# si "jour" a déjà été trouvé grâce à coreNLP
						if firstNounInTuple == nonAnnotedWord:
							#print(annotedWord)
							convTuple = list(v)
							convTuple[2] = annotedWord
							self.prepoSyntagm[k] = tuple(convTuple)

						if secondNounInTuple == nonAnnotedWord:
							convTuple = list(v)
							convTuple[1] = annotedWord
							self.prepoSyntagm[k] = tuple(convTuple)

				self.annotedPos["prepoSyntagm"] = (True, self.prepoSyntagm)#self.prepoSyntagm 

		#print(self.annotedPos["prepoSyntagm"])
		#print(self.annotedPos)


	# récupérer les annotations spécifiques à chaque catégorie grammaticale
	def getGramCategoryAnnotation(self):

		posAnnotations = {}
		for k,v in self.annotedPos.items():
			posAnnotations[k] = v[1]

		return posAnnotations



	# appliquer la bonne annotation à un mot suivant sa catégorie grammaticale
	def applyWordAnnotations(self, chosenWord, wordCategory):

		# vérifier si cette catégorie grammaticale a été annotée
		checkAnnotation = self.annotedPos[wordCategory][0]
		# récupération de l'annotation
		wordAnnotation = self.annotedPos[wordCategory][1]

		if checkAnnotation == True :
			# ajout de l'annotation du nom dans la phrase de sortie
			outPutWord = "[" + chosenWord + "](" + wordAnnotation + ")" 
		# si le nom d'origine n'avait pas d'annotation, on garde le nouveau nom sans annotation
		else:
			outPutWord = chosenWord

		return outPutWord


	def applyFollowingNomSyntAnnotations(self) :
		return self.annotedPos['followingNomSynt'][1]


	# appliquer l'annotation du syntagme prépositionnel
	def applyPrepSyntAnnotations(self, chosenPrepSynt) :

		outPutPrepSynt = ""
		joinedPrepSynt = ()
		
		prepSyntAnnoted = self.annotedPos['prepoSyntagm'][1]

		for number, prepSyntElements in prepSyntAnnoted.items() :
			joinedPrepSynt = joinedPrepSynt + prepSyntElements
			

		if len(chosenPrepSynt) == len(joinedPrepSynt) :
			for index, word in enumerate(joinedPrepSynt):
				searchAnnot = re.search('\[(.+?)\]\((.+?)\)', word)
				if searchAnnot :
					wordToAnnot = chosenPrepSynt[index]
					annot = searchAnnot.group(2)
					outPutPrepSynt = outPutPrepSynt + " " + "[" + wordToAnnot + "](" + annot + ")"
				else :
					word = chosenPrepSynt[index]
					outPutPrepSynt = outPutPrepSynt + " " + word

		else :

			for word in chosenPrepSynt :
				outPutPrepSynt = outPutPrepSynt + " " + word
			
				
		return outPutPrepSynt




class applyAnnotationsToYesOrNo :

	def __init__(self, sentence) :

		self.annotedWordsDico = {}
		# chercher tous les mots annotés dans la phrase d'entrée
		regexAnnotWords = r'(\[(\S+?(?: \S+)*)\]\((\w+)\))'
		# liste des mots annotés
		annotedWords = re.findall(regexAnnotWords, sentence)

		# comparer les mots/expressions annotées avec les part of speech de coreNLP
		for l in annotedWords:

			# groupe capturant correspondant à la version du mot débarassée du markdown (ex: [jour](time) --> jour)
			nonAnnotedWord = l[1]
	
			# groupe capturant correspondant à l'annotation (ex: [jour](time) -> time)
			wordAnnotation = l[2]

			# dictionnaire -> {mot : son annotation, ...}
			self.annotedWordsDico[nonAnnotedWord] = wordAnnotation


	def getAnnotDico(self) :
		return self.annotedWordsDico

		
	def getWordAnnotation(self, previousWord, newWord) :

		if previousWord in self.annotedWordsDico :
			annot = self.annotedWordsDico[previousWord]
			word = "[" + newWord + "](" + annot + ")"
		else :
			word = newWord

		return word







