# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path
import glob

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_configuration():
    config = dict()

    config['CORE_NLP_DIR'] = None
    config['CORE_NLP_PORT'] = None
    config['CORE_NLP_LANG'] = None
    config['GLAWI_BZ2'] = None
    config['GLAWI_PKL'] = None
    config['LEXICON_DIR'] = None
    config['DATA_AUGMENTATION_PORT'] = None
    config['SPACY_MODEL'] = None
    config['DATA_AUGMENTATION_PASSWORD'] = None

    print("Loading application parameters from .envdefault and .env files...")
    #https://github.com/TsuiJie/dotenv-python

    env_path = Path('.') / '.env'
    default_env_path = Path('.') / '.envdefault'

    try:
        with(open(default_env_path, 'r')) as file:
            for line in file:
                if line.startswith("#") == False and line.find('=') > -1:
                    variable = line.split('=')
                    config[variable[0].strip()] = variable[1].strip()

    except FileNotFoundError:
        print(".envdefault not exist in " + str(default_env_path.absolute()))

    try:
        with(open(env_path, 'r')) as file:
            for line in file:
                if line.startswith("#") == False and line.find('=') > -1:
                    variable = line.split('=')
                    config[variable[0].strip()] = variable[1].strip()
    except FileNotFoundError:
        print(".env not exist in " + str(env_path.absolute()))

    #Get parameters from system environment variables

    # CoreNLPServer parameters
    coreNLPDirectory = os.environ.get('CORE_NLP_DIR', config['CORE_NLP_DIR'])
    coreNLP_port = os.environ.get('CORE_NLP_PORT', config['CORE_NLP_PORT'])
    language = os.environ.get('CORE_NLP_LANG', config['CORE_NLP_LANG'])

    # glawi parameters
    glawiBz2FilePath = os.environ.get('GLAWI_BZ2', config['GLAWI_BZ2'])
    glawiPklFilePath = os.environ.get('GLAWI_PKL', config['GLAWI_PKL'])

    # lexicons directory
    lexiconsDirectory = os.environ.get('LEXICON_DIR', config['LEXICON_DIR'])

    # data augmentation port
    da_port = os.environ.get('DATA_AUGMENTATION_PORT', config['DATA_AUGMENTATION_PORT'])

    # spacy model path
    spacy_model_path = os.environ.get('SPACY_MODEL', config['SPACY_MODEL'])

    # application password
    password = os.environ.get('DATA_AUGMENTATION_PASSWORD', config['DATA_AUGMENTATION_PASSWORD'])

    if password == None or password == '':
        config['DATA_AUGMENTATION_PASSWORD'] = 'NO_PASSWORD'
    else:
        config['DATA_AUGMENTATION_PASSWORD'] = password


    print(config)

    try:
        coreNLP_port = int(coreNLP_port)
        config['CORE_NLP_PORT'] = coreNLP_port
    except TypeError:
        print('CORE_NLP_PORT is not configurated')
        sys.exit(1)

    if is_port_in_use(coreNLP_port) == True:
        print('The port ' + str(coreNLP_port) + " is already used by another application. Change the CORE_NLP_PORT parameter")
        sys.exit(1)

    try:
        da_port = int(da_port)
        config['DATA_AUGMENTATION_PORT'] = da_port
    except TypeError:
        print('DATA_AUGMENTATION_PORT is not configurated')
        sys.exit(1)

    if is_port_in_use(da_port) == True:
        print('The port ' + str(da_port) + " is already used by another application. Change the DATA_AUGMENTATION_PORT parameter")
        sys.exit(1)

    config['CORE_NLP_LANG'] = language
    if language != 'french':
        print('Only french language is currently supported. Put CORE_NLP_LANG = french')
        sys.exit(1)

    config['GLAWI_BZ2'] = glawiBz2FilePath
    try:
        existGlawiPath = os.path.exists(glawiBz2FilePath)
        if existGlawiPath == False:
            print(glawiBz2FilePath + " not exist. Please download the resource from http://redac.univ-tlse2.fr/lexiques/glawi/2016-05-18/GLAWI_FR_work_D2015-12-26_R2016-05-18.xml.bz2.")
            print("Configure GLAWI_BZ2 parameter with the correct path.")
            sys.exit(1)
    except TypeError:
        print("glawi ressource not exist. Please download the resource from http://redac.univ-tlse2.fr/lexiques/glawi/2016-05-18/GLAWI_FR_work_D2015-12-26_R2016-05-18.xml.bz2.")
        print("Configure GLAWI_BZ2 parameter with the correct path.")
        sys.exit(1)

    config['GLAWI_PKL'] = glawiPklFilePath
    try:
        glawiPikleDirectory = os.path.dirname(glawiPklFilePath)
        existGlawiPkleDirectory = os.path.exists(glawiPikleDirectory)
        if existGlawiPkleDirectory == False:
            print(glawiPikleDirectory + " not exist. Configure GLAWI_PKL parameter in an existing directory.")
            sys.exit(1)
    except TypeError:
        print("GLAWI_PKL parameter not configurated.")
        sys.exit(1)

    try:
        if lexiconsDirectory.endswith(os.sep) == False:
            lexiconsDirectory = lexiconsDirectory + os.sep
        lexiconsList = ['actions', 'informations', 'informations_yesOrNo']
        for lexicon in lexiconsList:
            if lexicon not in os.listdir(lexiconsDirectory):
                print(lexicon + " directory not in " + lexiconsDirectory + " Check you LEXICON_DIR parameter.")
                sys.exit(1)
    except AttributeError:
        print("LEXICON_DIR parameter not configurated.")
        sys.exit(1)
    config['LEXICON_DIR'] = lexiconsDirectory

    config['CORE_NLP_DIR'] = coreNLPDirectory
    try:
        if coreNLPDirectory.endswith(os.sep) == False:
            coreNLPDirectory = coreNLPDirectory + os.sep
        frenchJarModel = glob.glob(coreNLPDirectory +"*french*models.jar")
        coreNLPjar = glob.glob(coreNLPDirectory + "stanford-corenlp-*.jar")
        if len(coreNLPjar) == 0:
            print("stanford-corenlp-x.x.x.jar not exist in " + coreNLPDirectory + "\nDownload coreNLP from http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip")
            sys.exit(1)
        if len(frenchJarModel) == 0:
            print("stanford-french-corenlp-yyyy-mm-dd-models.jar not exist in " + coreNLPDirectory + "\nDownload the french model from http://nlp.stanford.edu/software/stanford-french-corenlp-2018-10-05-models.jar")
            sys.exit(1)
    except AttributeError:
        print("CORE_NLP_DIR parameter not configurated.")
        sys.exit(1)

    config['SPACY_MODEL'] = spacy_model_path
    try:
        if os.path.exists(spacy_model_path) == False:
            print(spacy_model_path + " not exist. Put the correct spacy path model")
            sys.exit(1)
    except TypeError:
        print("SPACY_MODEL parameter not configurated.")
        sys.exit(1)

    return config