# -*- coding: utf-8 -*-

# permet d'ajouter des listes externes aux listes utiles pour la reconnaissance
import os
def addKeyWordsResources(copiedList, finalList):
    with open(copiedList, "r") as fd:
        lines = fd.read().splitlines()
        for line in lines:
            finalList.append(line)


# ressources nécessaires pour les règles de commande
  # intégration des listes de mots et expressions pour la grammaire
def addGrammarResources(file, myRules):
    with open(file, "r") as fd:
      lines = fd.read().splitlines()
    # nettoyer la string "lexiques/fichier.txt" pour ne garder que le nom de la liste
    #file = file[9:]
    #file = file[:-4]
    file = os.path.basename(file)
    file = file.replace(".txt", "")
    for k,v in myRules.items():
      if k == "<" + file +">": #[0:-4]
        for line in lines:
            v.append(line)