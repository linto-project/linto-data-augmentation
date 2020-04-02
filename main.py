# -*- coding: utf-8 -*-

import configuration
from DataAugmentation import DataAugmentation

if __name__ == '__main__':

    config = configuration.get_configuration()
    system = DataAugmentation(coreNLPDirectory=config['CORE_NLP_DIR'], port=config['CORE_NLP_PORT'], language=config['CORE_NLP_LANG'],
                              glawiBz2FilePath=config['GLAWI_BZ2'], glawiPklFilePath=config['GLAWI_PKL'],
                              lexiconsDirectory=config['LEXICON_DIR'], spacyModelPath=config['SPACY_MODEL'])

  	## Call Data Augmentation
    commandFile = 'echantillon_commandes.md'  #'linto_sentences.md'   
    generatedCommandFile = 'generated_command.md'

    sentence =  "quelle est l'[actualité](news) [internationale](type_something) le mois prochain"
	#sentence = "[passe](action_start) en mode [huis-clos](recording)"
	#sentence = "[allume](action_on) la lumière blanche du salon"
	#sentence = "météo à [Marseille](location)"
	#sentence = "information importante "
	#sentence = "C'est quoi la météo à [Bastille](location)"
	#sentence = "joue la chanson l'étoile de Charles"
	#sentence = "[passe](action_start) en mode [huis-clos](recording)"
	#sentence = "[allume](action_on) la lumière blanche du salon"
	#sentence = "[allume](action_on) la lumière blanche du salon"

    #sentences = ["quelle est l'[actualité](news) [internationale](type_something) de la semaine dernière", "[passe](action_start) en mode [huis-clos](recording)"]
    #sentences = ["est-ce qu'il pleut","est-ce que la salle est [ouverte](meeting_free) maintenant", "est-ce qu'il va pleuvoir jusqu'à demain", "[Rennes](location) est-elle polluée", "va-t-il pleuvoir", "pleut-il", "la pollution à [Boston](location) est-elle élevée"]  
    #sentences = ["[monte](action_set_up) le [volume](audio) de [75](number) pourcent"]
    #sentences = ["est-ce que le temps est favorable pour une balade"]
    # sentences = ["quel temps fait-il à [Toulouse](location)"]
    sentences = ["quelle est la météo demain","est-ce qu'il a plu hier"]#["est-ce que la lumière bleue est allumée", "est-ce qu'il pleut", "est-ce qu'il va neiger"]#, "est-ce que la salle est ouverte maintenant", "est-ce qu'il pleut", "est-ce que le loup mange la chèvre"]
    
    # data augmentation for list
    for sent in sentences:
        similarSentences = system.data_augmentation_from_sentence(sent, limit=10)
        print("Original command: " + sent)
        for similarSentence in similarSentences:
            if similarSentence != sent:
                print("---Alternative command: " + similarSentence)

    # data augmentation for file
    # similarSentences = system.data_augmentation_file(commandFile, limit=10)
    # print(similarSentences)

    system.stopDASystem()