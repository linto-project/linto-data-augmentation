# -*- coding: utf-8 -*-
"""
Filter and Convert csv conceptNet data from https://github.com/commonsense/conceptnet5/wiki/Downloads to a pickle file as Word.py class
"""
import gzip
import re
from Word import Word
import pickle
import sys

words = dict()

def toId(word, category):
    id = word.replace(' ','_')

    if category != '':
        id = id + "_" + category

    id = id.lower()
    return id

def toCSVEntry(str):
    elements = str.split('\t')
    rel = elements[1]
    source = elements[2]
    target = elements[3]

    sourceForm = ''
    targetForm = ''
    sourceCategory = ''
    targetCategory = ''

    if source.endswith('/n') or source.endswith('/v') or source.endswith('/a') or source.endswith('/s') or  source.endswith('/r'):
        sourceForm = source[:-2].replace('/c/fr/','').replace('_',' ').strip()
        sourceCategory = source[len(source)-1:]
    else:
        sourceForm = source.replace('/c/fr/','').replace('_',' ').strip()

    if target.endswith('/n') or target.endswith('/v') or target.endswith('/a') or target.endswith('/s') or  target.endswith('/r'):
        targetForm = target[:-2].replace('/c/fr/','').replace('_',' ').strip()
        targetCategory = target[len(target)-1:]
    else:
        targetForm = target.replace('/c/fr/','').replace('_',' ').strip()

    line = sourceCategory + "\t" + source + "\t" + sourceForm + "\t" + rel + "\t" + targetCategory + "\t" + target + "\t" + targetForm + "\n"

    idSource = toId(sourceForm, sourceCategory)
    idTarget = toId(targetForm, targetCategory)

    sourceWord = None
    targetWord = None

    try:
        sourceWord = words[idSource]
    except KeyError:
        sourceWord = Word(sourceForm, sourceCategory)
        words[idSource] = sourceWord

    try:
        targetWord = words[idTarget]
    except KeyError:
        targetWord = Word(targetForm, targetCategory)
        words[idTarget] = targetWord


    sourceWord.add_relation(rel, targetWord)
    #sourceWord.print_relations_count()
    return line


if __name__ == '__main__':
    print (str(sys.getrecursionlimit()))
    #https://github.com/commonsense/conceptnet5/wiki/Relations
    pattern = re.compile('\/\w+\/\[\/r\/.+,\/c\/fr\/.+,\/c\/fr\/.+\]\t', re.IGNORECASE)

    #pattern2 = re.compile('\/\w+\/\[.+,\/c\/fr\/.+,\/c\/fr\/.+\]\t.+"surfaceText":.+', re.IGNORECASE)
    counter = 0
    fr_relations = open("./resource/conceptNet/conceptNet_fr.csv","w+", encoding='utf-8')
    synonym = open("./resource/conceptNet/conceptNet_synonym.csv","w+", encoding='utf-8')
    isa = open("./resource/conceptNet/conceptNet_isa.csv", "w+", encoding='utf-8')
    antonym = open("./resource/conceptNet/conceptNet_antonym.csv", "w+", encoding='utf-8')
    derivedFrom = open("./resource/conceptNet/conceptNet_derivedFrom.csv", "w+", encoding='utf-8')
    mannerOf = open("./resource/conceptNet/conceptNet_mannerOf.csv", "w+", encoding='utf-8')
    similarTo = open("./resource/conceptNet/conceptNet_similarTo.csv", "w+", encoding='utf-8')
    instanceOf = open("./resource/conceptNet/conceptNet_instanceOf.csv", "w+", encoding='utf-8')
    relatedTo = open("./resource/conceptNet/conceptNet_relatedTo.csv", "w+", encoding='utf-8')

    with gzip.open('./resources/conceptnet-assertions-5.7.0.csv.gz','rt', encoding='utf-8') as f:
        for line in f:
            if pattern.match(string=line):
                counter = counter + 1
                #print(line)
                entry = toCSVEntry(line)
                fr_relations.write(entry)
                if '/r/Synonym' in line:
                    synonym.write(entry)
                elif '/r/IsA' in line:
                    isa.write(entry)
                elif '/r/Antonym' in line:
                    antonym.write(entry)
                elif '/r/DerivedFrom' in line:
                    derivedFrom.write(entry)
                elif '/r/MannerOf' in line:
                    mannerOf.write(entry)
                elif '/r/SimilarTo' in line:
                    similarTo.write(entry)
                elif '/r/InstanceOf' in line:
                    instanceOf.write(entry)
                elif '/r/RelatedTo' in line:
                    relatedTo.write(entry)

    synonym.close()
    isa.close()
    antonym.close()
    derivedFrom.close()
    mannerOf.close()
    similarTo.close()
    relatedTo.close()
    fr_relations.close()
    sys.setrecursionlimit(50000)

    with open('./resources/conceptNet/conceptNet_fr.pickle', 'wb') as output:
        pickle.dump(words, output, pickle.HIGHEST_PROTOCOL)
    print('french relation: ' + str(counter))