# LinTO data augmentation

Python 3.6 projet for generating similar expressions from a LinTO french command corpus.

## Dependencies
Download the 2 next tools.

### GLAWI resource
GLAWI is a french lexical dictionary built from Wikitionary (http://redac.univ-tlse2.fr/lexiques/glawi.html).

 - http://redac.univ-tlse2.fr/lexiques/glawi/2016-05-18/GLAWI_FR_work_D2015-12-26_R2016-05-18.xml.bz2

### Stanford CoreNLP Tagger
Stanford CoreNLP is a java NLP toolkit (https://stanfordnlp.github.io/CoreNLP/)

 - http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
 - http://nlp.stanford.edu/software/stanford-french-corenlp-2018-10-05-models.jar

## Application configuration
You need to configure some variables before starting the application by setting environment variables or by creating a .env file on the same directory (a sample is available on .envdefault).

Application will read first .envdefault. It will then overload the variables with .env and finally from os environment variables.

 - **CORE_NLP_DIR**: Directory path for the unzipped stanford-corenlp-full-2018-10-05.zip.
 -  **CORE_NLP_PORT**: The port where CoreNLP will be run.
 - **CORE_NLP_LANG**: The command corpus language. For the moment only french language is supported.
 - **GLAWI_BZ2**: The path where GLAWI_FR_work_D2015-12-26_R2016-05-18.xml.bz2 is saved on disk
 - **GLAWI_PKL**: A path where a pickle file generated from the compressed GLAWI resource will be saved.
 - **LEXICON_DIR**: Directory path for the resources folder of the project.
 - **DATA_AUGMENTATION_PORT**: Application port
 - **DATA_AUGMENTATION_PASSWORD**: A password for the application. This password is need it to stop the application with a CURL query.
 - **SPACY_MODEL**: A path for the spacy french model resources. Please set the path for the /resources/spacy/fr_core_news_sm-2.1.0 directory.

 
## Running the application
### Setting the virtual environments
```
tar xvzf venv.tar.gz
source ./venv/bin/activate
```
### Start the API Rest server

```
./venv/bin/python data_augmentation_server.py
```

## Using the application
### Get similar command from a sentence:

Return at most 10 similar sentences from a LinTO sentence command.

```
curl -X POST 127.0.0.1:5000/dafromtext -F "limit=10" -F "text=quelle est l'[actualité](news) [internationale](type_something) le mois prochain"
```

**Expected results**:  In case the request is successfully executed a result in json is returned.

 - response: contains a list of similar LinTO sentence command
 - status: 200

In case the request fails, an explanation is retourned in the same json format

 - response: a detail of the error
 - status: 400 (HTTP code)

**Sample of a succeded results**:


```
{  
"response": [  
"cherche l'[actualité](news) [internationale](type_something) le mois prochain",  
"l'[actualité](news) [internationale](type_something) le mois prochain",  
"c'est quoi l'[actualité](news) [internationale](type_something) le mois prochain",  
"j'aimerais avoir l'[actualité](news) [internationale](type_something) le mois prochain",  
"j'aimerais connaître l'[actualité](news) [internationale](type_something) le mois prochain",  
"[actualité](news) [internationale](type_something) le mois prochain"  
],  
"status": 200  
}
```

### Get similar command from a markdown file:
Return at most 10 similar sentences for each LinTO command from cmd.md. Result will be saved in result.md file.

File content sample :

```
## intent:control
- [allume](action_on) la [lumière](light) de la salle
- [allumer](action_on) la [lumière](light) du salon
- [illumine](action_on) la [lampe](light)
- [éteindre](action_off) la [lumière](light)

## intent:chrono
- [start](action_start) le chrono
- peux tu [démarrer](action_start) le chronomètre
- peux tu [démarrer](action_start) le minuteur
- peux tu [commencer](action_start) le chrono
- peux tu [commencer](action_start) le minuteur
- peux tu [stopper](action_stop) le minuteur
- peux tu [stopper](action_stop) le chronomètre
- peux tu [stopper](action_stop) le chrono
- peux tu [arrêter](action_stop) le minuteur
- peux tu [arrêter](action_stop) le chronomètre
- [démarre](action_start) le minuteur pour [5](number) [minutes](time_unit)
- [débuter](action_start) le chronomètre pour [45](number) [minutes](time_unit)
- [démarre](action_start) le chrono pour [3](number) [heure](time_unit)
- [commence](action_start) le chrono pour [1](number) [heure](time_unit)
- [start](action_start) le chrono pour [2](number) [heures](time_unit)

## intent:pollution
- quel est le niveau de pollution à [bastia](location)
- quel est le niveau de pollution à [Toulouse](location)
- quel est le niveau de pollution à [Kyoto](location)
- quel est le niveau de pollution à [Seoul](location)
- donne moi le niveau de pollution à [Tokyo](location)
- donne moi le niveau de pollution à [Osaka](location)

## intent:news
- quels sont les événements [musicaux](type_musical) du [jour](time)
- quelle est l'actualité [musicale](type_musical) de la [semaine](time)
- quels sont les événements [politique](type_politique) du [jour](time)
- quels sont les événements [société](type_societe) de la [semaine](time)
- quels sont les événements [culturels](type_cultural) de la [semaine](time)
- quelles sont les actualités

```


```
curl -X POST 127.0.0.1:5000/dafromfile -F "limit=10" -F "file=@/path/to/linto/cmd.md" -o result.md
```

**Expected results**: In case the request is successfully executed a result in json is returned.

 - response: contains a markdown string with similar LinTO sentence command. For each original sentence, the system add *\<!-- Alternative Sentences -->* before the proposed similar LinTO sentence command
 - status: 200

In case the request fails, an explanation is retourned in the same json format

 - response: a detail of the error
 - status: 400, 404 or 406 (HTTP code)


### Stopping the service

Stopping the application with a specified password
```
curl -X POST 127.0.0.1:5000/shutdown?password=MY_PASSWORD
```

Stopping the application when no password was specified

```
curl -X POST 127.0.0.1:5000/shutdown
```

**Expected results**: If the application stop, a result in json is returned.

 - response: Application shutting down successfully
 - status: 200

In case the request fails, an explanation is retourned in the same json format

 - response: a detail of the error
 - status: 400 or 401 (HTTP code)
