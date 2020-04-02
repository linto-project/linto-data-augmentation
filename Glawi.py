# -*- coding: utf-8 -*-
from lxml import etree
from bz2 import BZ2File
import pickle
import os

########## Transformer GLAWI en dictionnaire clé-valeur

class Glawi:

	def __init__(self, glawiBz2FilePath, glawiPklFilePath):

		# Dictionnaire Glawi
		# word: {  gender : masc/fem,
		#  			number : sing/plur,
		#  			lemma : lemma,
		#  			inflection : 
		#  				{ 	Afpms : nourri
		#					Afpmp : nourris 
		#					Afpfs : nourrie  				  
		#  				}
		#  		}

		self.dico = {}

		pklFileExist = os.path.isfile(glawiPklFilePath)
		if pklFileExist:
			print("Reading from existing glawi pkl file")
			with open(glawiPklFilePath, 'rb') as input:
				self.dico = pickle.load(input)
		else:
			print("Initialise pkl file from glawi bz2 file")
			with BZ2File(glawiBz2FilePath) as xml_file:
				elements = etree.iterparse(xml_file, events=('start','end'))
				inflections = {}
				gender = ""
				number = ""
				lemma = ""
				currentEntry = ""
				currentEntryType = ""
				checkCurrentEntry = False


				for event, element in elements:

					if event == "start":
						if element.tag == "title":

							checkCurrentEntry = False

							lemma = ""
							gender, number = "", ""
							inflections = {}


							currentEntry = element.text

						# lemme
						try:
							if element.tag == "inflectedForm":
								lemma = element.attrib["lemma"]
						except KeyError:
							lemma = ""
					
						# genre/nombre
						try:

							if element.tag == "pos":
								gramCategory = element.attrib["type"]
								if gramCategory != "verbe":
									gender = element.attrib["gender"]
									number = element.attrib["number"]
								else:
									gender = ""
									number = ""

								inflections = {}
								currentEntryType = str(currentEntry) + "_" + str(gramCategory)

								checkCurrentEntry = True

						except KeyError:
							gender = ""
							number = ""

						# flexions
						try:
							if element.tag == "inflection":
								inflections[element.attrib["gracePOS"]] = element.attrib["form"]

						except:
							pass

						if currentEntryType != "" and checkCurrentEntry == True:

							if (gender != "") and (number != ""):
								gender, number = gender, number
							else:
								gender, number = "",""
							

							if lemma != "":
								lemma = lemma
							else:
								lemma = ""

							self.dico[currentEntryType] = {"lemma":lemma, "gender":gender, "number":number, "inflections":inflections}

					element.clear()

			with open(glawiPklFilePath, 'wb') as output:
				pickle.dump(self.dico, output, pickle.HIGHEST_PROTOCOL)


	# récupérer Glawi sous la forme d'un dictionnaire clé-valeur
	def getDictionary(self):
		return self.dico

	# récupérer l'objet GLawi correspondant à un mot 
	def getGlawiObject(self, word):
		glawiObj = self.dico[word]
		return glawiObj


	## RECUPERATION DES FORMES FLECHIES

	# récupérer la forme fléchie d'un adjectif selon le nom qui l'accompagne
	def getAdjectiveInflection(self, adjective, genderNoun, numberNoun):

		glawiObjectAdjective = self.dico[adjective + "_adjectif"]
		glawiObjectGenderNumber = "Afp" + genderNoun + numberNoun
		adjective = glawiObjectAdjective['inflections'][glawiObjectGenderNumber]

		return adjective


	## RECUPERATION DU GENRE ET NOMBRE DES NOMS

	# récupérer le genre et nombre du nom de la phrase d'entrée
	def getInputNounGenderNumber(self,noun):

		glawiObjectNoun = self.dico[noun]
		gender = glawiObjectNoun["gender"]
		number = glawiObjectNoun["number"]

		if gender == "":
			gender = "m"

		if number == "":
			number = "s"

		nounGenderNumber = "gender=" + gender + "|number=" + number

		return nounGenderNumber


	# récupérer le genre et nombre des synonymes du nom principale de la phrase d'entrée
	def getNounSynonymsGenderNumber(self, synonymsList):

		nounSynonymsGenNum = []
		#print (nounSynonyms)
		for noun in synonymsList:
			if noun != "original_$" :
				try:
					glawiObjectNoun = self.dico[noun + "_nom"]
					gender = glawiObjectNoun["gender"]
					number = glawiObjectNoun["number"]
				except KeyError:
					gender = ""
					number = ""
			

				nounGenderNumber = "gender=" + gender + "|number=" + number
				nounSynonymsGenNum.append(noun + "_" + nounGenderNumber)
				
		nounSynonymsGenNum.append('original_$')

		return nounSynonymsGenNum


	# récupérer le genre/nombre d'un part of speech sujet
	def getSubjGenderNumber(self, subject, subjGramCat) :

		# si le sujet est un nom
		if subjGramCat == "NOUN" :
			subjGramCat = "_nom"
			# récupérer son genre / nombre
			try :
				subjGender = self.dico[subject + subjGramCat]['gender']
				subjNumber = self.dico[subject + subjGramCat]['number']
			except KeyError :
				subjGender = "m"
				subjNumber = "s"

		# si le sujet est un pronom
		elif subjGramCat == "PRON" :
			if subject == "il" :
				subjGender = "m"
				subjNumber = "s"
			elif subject == "elle" :
				subjGender = "f"
				subjNumber = "s"
			elif subject == "ils" :
				subjGender = "m"
				subjNumber = "p"
			elif subject == "elles" :
				subjGender = "f"
				subjNumber = "p"

		# si le sujet est un nom propre
		elif subjGramCat == "PROPN" :
			subjGender = "m"
			subjNumber = "s"

		else :
			subjGender = "m"
			subjNumber = "s"


		genNum = (subjGender, subjNumber)

		return genNum


	def getInflection(self, pos, posGramCat, subjGen, subjNum) :
		
		if posGramCat != "determinant" :
			if posGramCat == "adjectif" :
				glawiCat = "adjectif"
				inflection = "Afp" + subjGen + subjNum
			elif posGramCat == "pp" :
				glawiCat = "verbe"
				inflection = "Vmps-" + subjNum + subjGen
			elif posGramCat == "verbe" :
				glawiCat = "verbe"
				inflection = "Vmip3" + subjNum + "-"

			# récupérer le lemme du part of speech
			# wordInDico = self.dico[pos + glawiCat]
			# posLemma = wordInDico['lemma']
			posLemma = self.getWordLemma(pos, glawiCat)

			try :
				# chercher le lemme dans Glawi
				wordLemInDico = self.dico[posLemma + "_" + glawiCat]
				# trouver la liste des flexions
				inflections = wordLemInDico["inflections"]
				# trouver la flexion qui nous intéresse
				inflectedWord = inflections[inflection]
			except KeyError :
				inflectedWord = pos
		

		# else :
		# 	if subjGen == "m" and subjNum == "s" :
		# 		inflectedWord = "le"
		# 	elif subjGen == "f" and subjNum == "s" :
		# 		inflectedWord = "la"
		# 	elif subjNum == "p" :
		# 		inflectedWord = "les"

		return inflectedWord


	## récupérer le lemme d'un mot
	def getWordLemma(self, word, gramCategory):

		try :
			glawiObjectWord = self.dico[word + "_" + gramCategory]
			wordLemma = glawiObjectWord['lemma']
			if wordLemma == "" :
				wordLemma = word
		except KeyError :
			wordLemma = word

		return wordLemma


	# récupérer le pronom correspondant à un nom
	def getPronoun(self, word) :
		
		try :
			wordGender = self.dico[word]['gender']
			wordNumber = self.dico[word]['number']
		except KeyError :
			wordGender = ""
			wordNumber = ""

		if wordGender == "m" and wordNumber == "s" :
			pronoun = "il"
		elif wordGender == "m" and wordNumber == "p" :
			pronoun = "ils"
		elif wordGender == "f" and wordNumber == "s" :
			pronoun = "elle"
		elif wordGender == "f" and wordNumber == "p" :
			pronoun = "elles"
		elif wordGender == "" and wordNumber == "" :
			pronoun = "il(s)/elle(s)"
		elif wordGender == "f" and wordNumber == "sp" :
			pronoun = "elle"
		elif wordGender == "m" and wordNumber == "sp" :
			pronoun = "il"
		else :
			pronoun = "il(s)/elle(s)"

		return pronoun

