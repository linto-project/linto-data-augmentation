# -*- coding: utf-8 -*-
from flask import request, Flask, jsonify
from flask_api import status
from DataAugmentation import DataAugmentation
import configuration
import re
import content_parser

app = Flask(__name__)

config = configuration.get_configuration()

system = DataAugmentation(coreNLPDirectory=config['CORE_NLP_DIR'], port=config['CORE_NLP_PORT'],
                          language=config['CORE_NLP_LANG'],
                          glawiBz2FilePath=config['GLAWI_BZ2'], glawiPklFilePath=config['GLAWI_PKL'],
                          lexiconsDirectory=config['LEXICON_DIR'], spacyModelPath=config['SPACY_MODEL'])

password = config['DATA_AUGMENTATION_PASSWORD']

@app.route("/dafromtext", methods=['POST'])
def data_augmentation_from_text():

    if request.method == 'POST':
        sentence = request.form['text']
        limit = request.form.get('limit')

        if sentence == None:
            response = jsonify({"response": "text parameter not found. Valid syntax: CURL -X POST ip:port/dafromtext -F 'limit=LIMIT' -F 'text=intent command", "status": 400}), 400
            return response

        if limit == None:
            limit = 10
        try:
            limit = int(limit)
        except ValueError:
            response = jsonify({"response": "limit parameter is not integer", "status": 400}), 400
            return response

        cleaned_sentence = ""

        try:
            cleaned_sentence = content_parser.parse_intent_text_command(sentence)
        except SyntaxError as error:
            response = jsonify({"response": str(error), "status": 400}), 400
            return response

        similarSentences = system.data_augmentation_from_sentence(cleaned_sentence, limit=limit)

        response = jsonify({"response": list(similarSentences), "status":200}), 200
        return response

    response = jsonify({"response": "Not valid query. Valid syntax: CURL -X POST ip:port/dafromtext -F 'limit=LIMIT' -F 'text=intent command", "status": 400}), 400
    return response

@app.route("/dafromfile", methods=['POST'])
def data_augmentation_from_file():

    limit = request.form.get('limit')
    if limit == None:
        limit = 10
    try:
        limit = int(limit)
    except ValueError:
        response = jsonify({"response": "limit parameter is not integer", "status": 400}), 400
        return response

    if request.method == 'POST':
        file = None
        try:
            file = request.files['file']
        except IOError:
            response = jsonify({"response": "file resource not exist", "status": 404}), 404
            return response
        if re.match('^\s+$',file.filename, re.MULTILINE) != None or file.filename == None:
            response = jsonify({"response": "file parameter not contains a file path", "status": 404}), 404
            return response
        if not allowed_file(file.filename):
            response = jsonify({"response": "file parameter is not a markdown file. Your file must have md extension", "status": 406}), 406
            return response
        else:
            content = file.read()
            cleaned_markdown = ""
            try:
                content = content.decode('utf-8', errors = 'strict')
            except UnicodeDecodeError as error:
                response = jsonify({"response": file.filename + " not in UTF-8 encoding. " + str(error), "status": 406}), 406
                return response

            try:
               cleaned_markdown = content_parser.parse_markdown_content(content)
            except SyntaxError as error:
                response = jsonify({"response": "Syntax error in " + file.filename + ". " + str(error), "status": 400}), 400
                return response

            result = system.data_augmentation_from_markdown(cleaned_markdown, limit=limit)
            response = jsonify({"response": result, "status": 200}), 200
            return response

    response = jsonify({"response": "Not valid query. Syntax: CURL -X POST ip:port/dafromfile -F 'limit=LIMIT' -F 'file=@/path/to/your/file.md'", "status": 400}), 400
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['md', 'MD']

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    system.stopDASystem()
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():

    app_password = request.args.get('password')

    if password == 'NO_PASSWORD':
        shutdown_server()
        response=jsonify({"response":"Application shutting down successfully","status":200}), 200
        return response
    elif app_password == password:
        shutdown_server()
        response=jsonify({"response":"Application shutting down successfully","status":200}), 200
        return response
    else:
        if app_password == None:
            response = jsonify({"response": "password parameter not exist in the query. Syntax: /shutdown?password=YOUR_PASSWORD", "status": 400}), 400
            return response
        else:
            response=jsonify({"response":"Wrong password. Application not stopped","status":401}), 401
            return response

if __name__ == "__main__":

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_AS_ASCII'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.run(debug=False, port=config['DATA_AUGMENTATION_PORT'])
