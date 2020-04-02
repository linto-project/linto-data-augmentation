class GrammaticalRules:

    # déterminant, nom, adjectif, genre/nombre du nom, syntagme prépositionnel, lemme du verbe, lemme de l'adjectif
    def __init__(self):

        self.rulesAction = { '<start>'    : ['<template>'],
            # REGLES
            '<template>' : [
            # tu pourrais allumer la lumière
            '<interro_infinitive> <verb> <det> <noun>',
            # est-ce que tu pourrais allumer la lumière
            '<interro_adverb> <post_interro_ability> <verb> <det> <noun>',
            # allume la lumière
            '<verb_tense_impe> <det> <noun>',
            # allumer la lumière
            '<verb> <det> <noun>',
            # j'aimerais que tu allumes la lumière 
            '<interro_subj> <verb_tense_subj> <det> <noun>', #'<interro_commande_subj> <pronouns> <verbe_subj> <noun>'
            ],

          
            # les interro suivis d'un infinitif (récup dans fichier)
            '<interro_infinitive>'  : [],
            # le verbe récupéré dans la phrase d'origine ou un synonyme
            '<verb>'     : ['original_$'],
            # le nom récupéré dans la phrase d'origine ou synonyme
            '<noun>'     : ['original_$'],
           
            # les interro suivis de verbes de capacité
            '<interro_adverb>'     : [],
            # les verbes et expressions de capacités
            '<post_interro_ability>' : [],

            # liste des expressions figées suivies d'un subjonctif
            '<interro_subj>' : [],

            # liste des synonymes de l'adjectif principal
            '<adjective>': ['original_$'],

            # liste des adverbes de temps
            '<adverb_time>': ['original_$']
           

          }


        self.rulesInfo = { '<start>'    : ['<template>'],
            # REGLES
            '<template>' : [
            # c'est quoi la température
            '<interro_sn> <det> <noun>',
            # quel/comment est la température
            '<interro_determinant> <verb_auxiliary> <det> <noun>',
            # pourrais-tu montrer la température
            '<interro_infinitive> <verb_demo> <det> <noun>',
            # température
            '<noun>',
            # la température
            '<det> <noun>'
            ], 

            # c'est quoi, cherche ... + syntagme nominal
            '<interro_sn>' : [],
            '<noun>' : ['original_$'],
            # merci de, tu pourrais... + infinitif
            '<interro_infinitive>' : [],
            # afficher, montrer...
            '<verb_demo>' : [],
            # liste des synonymes de l'adjectif principal
            '<adjective>': ['original_$']

            }


        self.rulesInfoYesOrNo = { '<start>'    : ['<template>'],
            # REGLES
            '<template>' : [
            #est-ce que la salle est libre
            'est-ce que <sentence>',
            # dis-moi si la salle est libre
            '<interro_if> <sentence>',
            # la salle est libre
            '<sentence>',
            #la salle est-elle libre
            '<sentence_inverted_subj>'

            ],

            '<interro_if>' : []

            }
        


    def getActionRules(self):
        return self.rulesAction

    def getInformationRules(self):
        return self.rulesInfo

    def getInformationYesOrNoRules(self):
        return self.rulesInfoYesOrNo