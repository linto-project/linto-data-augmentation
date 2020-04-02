# -*- coding: utf-8 -*-
import re
import random

class loadYesOrNoQuestionGrammar :

	def __init__(self, glawi, questionType, depParsing, ruleSet, sentenceElements, annotations) :

		self.grammar = {}
		self.regex = '<\w+>'
		for rule in ruleSet:
			self.addRuleInYesOrNo(rule, ruleSet[rule])

		# morceau de phrase qui vient après mot interrogatif "est-ce que"
		# ou interrogation totale ayant une autre structure syntaxique
		sentence = ""
		for pos in sentenceElements :
			sentence = sentence + pos[0] + " "
		self.sentence = sentence
		# part of speech sans le mot interrogatif
		self.pos = sentenceElements

		# parsing en dépendance
		self.depParsing = depParsing
		# le dictionnaire Glawi et ses méthodes
		self.glawi = glawi
	
		# type de question (identifiée par les patrons syntaxiques du NLPEngine)
		self.questionType = questionType
		self.annotations = annotations


	def addRuleInYesOrNo(self, ruleName, ruleContent):
		if re.match(self.regex, ruleName) == None:
			raise Exception('Malformed rule name.')
		if type(ruleContent) is not list:
			raise Exception('Rule content must be a list.')
		if ruleName not in self.grammar:
			self.grammar[ruleName] = ruleContent
		else:
			raise Exception('Rule already exists.')


	# choisir un synonyme pour un mot donné
	def getSynonyms(self, word, gramCat) :
		
		newWord = ""
		# liste des auxiliaires et semi-auxiliaires (à ne pas modifier)
		aux = ["être", "avoir" ,"devoir", "pouvoir", "faire"]

		synoNoun = ["original_$"]
		synoAdj = ["original_$"]
		synoVerb = ["original_$"]
		sentence = ""

		if gramCat == "NOUN" :
			# noun_synonyms_list = self.DicoGenerator.get_most_similar_words(word,"n")
			# synoNoun.expand(noun_synonyms_list)
			synonym = random.sample(synoNoun, 1)[0]

		elif gramCat == "ADJ" :
			# adjective_synonyms_list = self.DicoGenerator.get_most_similar_words(word,"a")
			# synoAdj.expand(adjective_synonyms_list)
			synonym = random.sample(synoAdj, 1)[0]

		elif gramCat == "VERB" :
			verbLemma = self.glawi.getWordLemma(word, "verbe")
			# verb_synonyms_list = self.DicoGenerator.get_most_similar_words(verbLemma,"v")
			
			if verbLemma not in aux :
				synonym = random.sample(synoVerb, 1)[0]
			else :
				synonym = "original_$"
	

		if synonym != "original_$":
			newWord = (word, synonym, gramCat)
		elif synonym == "original_$":
			newWord = (word, word, gramCat)

		return newWord


	# trouver le sujet d'origine d'un POS
	def getOriginSubject(self, originPos) :
		
		originSubj = ""
		# chercher la relation "nsubj" et l'adjectif d'origine dans les dépendances
		for dp in self.depParsing :
			if dp[0] == "nsubj" and dp[1] == originPos : 
				# récupérer le sujet d'origine
				originSubj = dp[2]
			if dp[0] == "amod" and dp[2] == originPos :
				originSubj = dp[1]

			if dp[0] == "det" and dp[2] == originPos :
				originSubj = dp[1]

			# relation participe passé
			# récupérer la relation 'auxpass' entre l'auxiliaire et le participe passé
			if dp[0] == "nsubjpass" and dp[1] == originPos :
				# récupérer le nsubjpass entre le participe passé et le sujet
				originSubj = dp[2]
	
		return originSubj


	# trouver le nouveau sujet synonyme d'un POS à partir de son sujet d'origine
	def getNewSubject(self, newPosList, originSubj) :

		newSubjGramCat = ""
		newSubj = ""
		subjAndGramCat = ("", "")
		if originSubj != "" :
			# chercher ce sujet d'origine dans la liste des nouveaux POS
			for nPos in newPosList :
				# récupérer le nouveau sujet synonyme choisi
				if nPos[0] == originSubj :
					newSubjGramCat = nPos[2]
					if newSubjGramCat == "PRON" or newSubjGramCat == "PROPN":
						newSubj = originSubj
					else :
						newSubj = nPos[1]
		

			subjAndGramCat = (newSubj, newSubjGramCat)

		return subjAndGramCat


	# fléchir un part of speech selon son sujet
	def inflectPos(self, subject, subjGramCat, pos, posGramCat) :

		if subject != "" and subjGramCat != "" :
			subjGenNum = self.glawi.getSubjGenderNumber(subject, subjGramCat)
			subjGen = subjGenNum[0]
			subjNum = subjGenNum[1]
			inflectedWord = self.glawi.getInflection(pos, posGramCat, subjGen, subjNum)

		else :
			inflectedWord = pos

		return inflectedWord


	# fléchir le déterminant selon le nom qui l'accompagne 
	def getDetInflection(self, subject, subjGramCat, det) :

		# récupérer le genre/nombre de ce nom sujet
		subjGenNum = self.glawi.getSubjGenderNumber(subject, subjGramCat)
		subjGen = subjGenNum[0]
		subjNum = subjGenNum[1]

		if subjNum == "sp" :
			subjNum = "s"

		defini_det = {"ms" : "le", "fs" : "la", "fp" : "les", "fp" : "les"}
		indefini_det = {"ms" : "un", "fs" : "une", "fp" : "des","mp" : "les"}
		demonstratif_adj = {"ms" : "ce", "fs" : "cette", "fp" : "ces", "mp" : "les"}
		possessif_adj1 = {"ms" : "mon", "fs" : "ma", "fp" : "mes", "mp" : "les"}
		possessif_adj2 = {"ms" : "ton", "fs" : "ta", "fp" : "tes", "mp" : "les"}
		possessif_adj3 = {"ms" : "son", "fs" : "sa", "fp" : "ses", "mp" : "les"}
		possessif_adj4 = {"ms" : "notre", "fs" : "notre", "fp" : "nos", "mp" : "les"}
		possessif_adj5 = {"ms" : "votre", "fs" : "votre", "fp" : "vos", "mp" : "les"}
		possessif_adj6 = {"ms" : "leur", "fs" : "leur", "fp" : "leurs", "mp" : "les"}

		# vérifier dans quelle catégorie le déterminant actuel se situe
		# choisir une nouvelle flexion selon le g/n dans la bonne catégorie
		try :
			if det in defini_det.values() :
				inflectedDet = defini_det[subjGen + subjNum]
			elif det in indefini_det.values() :
				inflectedDet = indefini_det[subjGen + subjNum]
			elif det in demonstratif_adj.values() :
				inflectedDet = demonstratif_adj[subjGen + subjNum]
			elif det in possessif_adj1.values() :
				inflectedDet = possessif_adj1[subjGen + subjNum]
			elif det in possessif_adj2.values() :
				inflectedDet = possessif_adj2[subjGen + subjNum]
			elif det in possessif_adj3.values() :
				inflectedDet = possessif_adj3[subjGen + subjNum]
			elif det in possessif_adj4.values() :
				inflectedDet = possessif_adj4[subjGen + subjNum]
			elif det in possessif_adj5.values() :
				inflectedDet = possessif_adj5[subjGen + subjNum]
			elif det in possessif_adj6.values() :
				inflectedDet = possessif_adj6[subjGen + subjNum]
			else :
				inflectedDet = "le/la/les"
		except KeyError :
			inflectedDet = "le/la/les"

		return inflectedDet


	# vérifier si un part of speech identifié comme "verbe" est un verbe ou un participe passé
	# cas 1 : "il va neiger" -> "neiger" identifié par CoreNLP comme verbe -> verbe
	# cas 2 : "la porte est ouverte" -> "ouverte" identifié comme verbe -> participe passé
	def checkVerb(self, verb) :
		
		# verbe par défaut
		gramCat = "verbe"

		for dp in self.depParsing :
			verbOrppInDp = dp[1]
			auxInDp = dp[2]
			if verbOrppInDp == verb and (dp[0] == "auxpass" or dp[0] == "aux"):
				# récupérer le lemme de l'auxiliaire
				auxLemma = self.glawi.getWordLemma(auxInDp, "verbe")
				# vérifier si le verbe "aux" est le verbe être ou le verbe "avoir"
				if auxLemma == "être" or auxLemma == "avoir" :
					# si c'est le cas, le mot dépendant de l'auxiliaire est un participe passé
					gramCat = "pp"
				# si c'est un verbe autre que les auxiliaires être/avoir (ex: aller -> semi-auxiliaire)
				else :
					# le dépendant un verbe à garder à l'infinitif (ex: il va neiger -> il va pleuvoir)
					gramCat = "infinitif_verbe"

		return gramCat


	# fléchir les part of speech
	def inflectingPartsOfSpeech(self, newPosList) :
		
		newInflectedPos = []
	
		# dans la liste des nouveaux part of speech choisis -> (ancien pos, nouveau pos, catégorie grammaticale)
		for newPos in newPosList :

			# on garde certains part of speech inchangés
			if newPos[1] == "" and newPos[2] != "DET" :
				word = newPos[0]
				newInflectedPos.append((newPos[0], word, newPos[2]))
			# le nom n'est pas fléchi
			elif newPos[2] == "NOUN":
				word = newPos[1]
				newInflectedPos.append((newPos[0], word, newPos[2]))

			# les autres part of speech sont fléchis
			else :

				posList = ["ADJ", "VERB"]
				# on fléchit les verbes, adjectifs et déterminants :
				if newPos[2] == "ADJ" :
					posGramCat = "adjectif"
				elif newPos[2] == "VERB" :
					# on vérifie si le verbe identifié est un verbe ou un participe passé
					posGramCat = self.checkVerb(newPos[0])
				elif newPos[2] == "DET" :
					posGramCat = "determinant"


				if newPos[2] in posList :
					# garder les verbes qui suivent un semi-auxiliaire à l'infinitif
					if posGramCat == "infinitif_verbe" :
						newInflectedPos.append((newPos[0], newPos[0], newPos[2]))
					# pour les autres part of speech
					else :
						# récupérer le mot d'origine 
						originWord = newPos[0]
						# récupérer le sujet d'origine de ce part of speech
						originSubj = self.getOriginSubject(originWord)
						# en déduire le nouveau sujet (sujet synonyme)
						newSubj = self.getNewSubject(newPosList, originSubj)
						# récupérer le genre / nombre de ce sujet
						inflectedWord = self.inflectPos(newSubj[0], newSubj[1], newPos[1], posGramCat)
						# ajouter le nouveau mot fléchi à la liste
						newInflectedPos.append((newPos[0], inflectedWord, newPos[2]))


				elif newPos[2] == "DET" :
					originDet = newPos[0]
					originSubj = self.getOriginSubject(originDet)
					newSubj = self.getNewSubject(newPosList, originSubj)
					if originSubj != newSubj[0] :				
						inflectedDet = self.getDetInflection(newSubj[0], newSubj[1], originDet)
						newInflectedPos.append((newPos[0], inflectedDet, newPos[2]))
					else :
						inflectedDet = originDet
						newInflectedPos.append((newPos[0], inflectedDet, newPos[2]))
		

		return newInflectedPos


	# assembler les nouveaux part of speech fléchis et leur rendre leurs annotation
	def getEntireSentence(self, inflectedPos) :

		sentence = ""
		for word in inflectedPos :
			previousWord = word[0]
			newWord = word[1]
			word = self.annotations.getWordAnnotation(previousWord, newWord)
			sentence = sentence + word + " "
			
		return sentence


	## REMPLACER LES ELEMENTS DE REGLES

	# "la salle est-elle libre" -> "la salle est libre"
	def replaceBySentence(self) :

		sentence = []
		partsOfSpeech = {}
		importantPos = ["VERB","NOUN", "ADJ"]
		notNeededInSent = ["PRON"]#, "DET"]

		# vérifier si la phrase est de type "la salle est-elle libre"
		if self.questionType == "SN_V_PRON" :
			for index, p in enumerate(self.pos, start=1):
				# récupérer la catégorie grammaticale du mot actuel
				gramCat = p[1]
				# récupérer le mot
				w = p[0]

				if gramCat in importantPos :
					synonym = self.getSynonyms(w, gramCat)
					sentence.append(synonym)
				elif gramCat in notNeededInSent :
					pass	
				else: 
					sentence.append((w, "", gramCat))


		# phrase type "(est-ce que) la salle est libre"
		elif self.questionType == "SN_V":
			for index, p in enumerate(self.pos, start=1):
				# récupérer la catégorie grammaticale du mot actuel
				gramCat = p[1]
				# récupérer le mot
				w = p[0]

				# on ne s'intéresse qu'aux part of speech de la liste
				if gramCat in importantPos :
					synonym = self.getSynonyms(w, gramCat)
					sentence.append(synonym)
				elif gramCat in notNeededInSent :
					pass
				else :
					sentence.append((w, "", gramCat))

		# "(est-ce qu') il neige"
		elif self.questionType == "PRON_V" :
			for index, p in enumerate(self.pos, start=1):
				gramCat = p[1]
				w = p[0]
				if gramCat in importantPos :
					synonym = self.getSynonyms(w, gramCat)
					sentence.append(synonym)
				# elif gramCat in notNeededInSent :
				# 	pass
				else :
					sentence.append((w, "", gramCat))

					

		# phrase type "neige-t-il"
		elif self.questionType == "V_PRON" :

			# récupérer le pronom -> "il"
			pronoun = self.pos[1][0]
			clearPron = re.search(r'\b(je|tu|il|elle|nous|vous|ils|elles)\b', pronoun)

			if clearPron :
				pronoun = clearPron.group(0)
				sentence.append((pronoun, "", "PRON"))
		
			for index, p in enumerate(self.pos, start=1):
				# récupérer la catégorie grammaticale du mot actuel
				gramCat = p[1]
				# récupérer le mot
				w = p[0]

				if gramCat in notNeededInSent :
					pass
				else :
					sentence.append((w, "", gramCat))

		# renvoyer les part of speech fléchis
		inflectedPos = self.inflectingPartsOfSpeech(sentence)


		return inflectedPos

	# est-ce que la salle est libre -> la salle est-elle libre
	def replaceByInvertedSubj(self, inflectedPos) :

		invertedSubjSent = []

		# vérifier si la phrase commence par un syntagme nominal
		if inflectedPos[0][2] == "DET" and inflectedPos[1][2] == "NOUN" : 
			# vérifier le genre/nombre du nom
			noun = self.pos[1][0] + "_nom"
			# donner un pronom correspondant
			pronoun = self.glawi.getPronoun(noun)

			# ajouter le déterminant
			invertedSubjSent.append(inflectedPos[0])
			# le nom
			invertedSubjSent.append( inflectedPos[1])

			if inflectedPos[2][2] == "VERB" or inflectedPos[2][2] == "AUX" :
				verb = inflectedPos[2][1]

				lastVerbChar = verb[-1:]
				index = 3

			elif inflectedPos[2][2] == "ADJ" :
				if (inflectedPos[3][2] == "VERB" or inflectedPos[3][2] == "AUX") :
					verb = inflectedPos[3][1]
					lastVerbChar = verb[-1:]
					index = 4

		# si la phrase commence par un pronom
		elif inflectedPos[0][2] == "PRON" :
			
			pronoun = inflectedPos[0][1]
			verb = inflectedPos[1][1]
			lastVerbChar = verb[-1:]
			index = 2

		elif inflectedPos[0][2] == "PROPN" :

			pronoun = "il"
			verb = inflectedPos[1][1]
			lastVerbChar = verb[-1:]
			index = 2
			invertedSubjSent.append(inflectedPos[0])

		# ajout de la liaison si le verbe ne finit pas par "t"
		if lastVerbChar == "t" :
			invertedSubjSent.append((verb, verb + "-" + pronoun, "VERB"))
		else :
			invertedSubjSent.append((verb, verb + "-t-" + pronoun, "VERB"))

		# ajout du reste de la phrase
		for i in range(index, len(inflectedPos)) :
			invertedSubjSent.append(inflectedPos[i])

		return invertedSubjSent



	def replace(self, ruleContent):
	
		result = ruleContent
		words = ruleContent.split()
		sentence = ""

		for word in words:

			# "la salle est-elle libre" -> "la salle est libre"
			if word == '<sentence>' :

				inflectedPos = self.replaceBySentence()
				#result = self.replaceBySentence(result, word)
				sentence = self.getEntireSentence(inflectedPos)
				result = result.replace(word, sentence)

			# "la salle est libre" -> "la salle est-elle libre"
			elif word == '<sentence_inverted_subj>' :

				if self.questionType != "SN_V_PRON" :
					inflectedPos = self.replaceBySentence()
					invertedSubjSent = self.replaceByInvertedSubj(inflectedPos)
					sentence = self.getEntireSentence(invertedSubjSent)
					result = result.replace(word, sentence)
				else :
					result = result.replace(word, "")

			elif word in self.grammar and re.match(r'<\w+>',word):
				newValue = random.sample(self.grammar[word], 1)[0]
				result = result.replace(word, newValue, 1)

		return result
        

	# générer la nouvelle phrase
	def generateSimilarExpression(self, startRule):

	    if len(self.grammar) == 0:
	        raise Exception('Empty grammar.')
	    start = self.grammar.get(startRule)
	    if start == None:
	        raise Exception('Start rule not in grammar.')
	    generatedString = startRule 
	  
	    while generatedString.find('<') != -1:
	        generatedString = self.replace(generatedString)

	    # régler les liaisons des voyelles
	    generatedString = self.vowelsAndSpaces(generatedString)
	    
	    return generatedString.lstrip(' ')


	def vowelsAndSpaces(self, generatedString) :	
		# traiter les "de le" laissés par coreNLP et les remplacer par "du"
		sil = re.compile('(^|\s)si il\s')
		generatedString = sil.sub('\\1s\'il ', generatedString)

		quil = re.compile('(^|\s)que ([hâaeéèêiîïouy])')
		generatedString = quil.sub('\\1qu\'\\2', generatedString)

		l = re.compile('l\' ')
		generatedString = l.sub('l\'', generatedString)

		return generatedString
