# -*- coding: utf-8 -*-
import re

def valid_intent_definition(intent_definition):
    #print(intent_definition + " " + str(re.match("^## +intent:[a-zA-Z0-9_\-]+ *$", intent_definition, re.MULTILINE)))
    if re.match("^## +intent:[a-zA-Z0-9_\-]+ *$", intent_definition, re.MULTILINE) == None:
        return False
    return True

def valid_intent_text_command(i, intent_text_commad):
    countOpenEntityInstance = len(re.findall("\[", intent_text_commad))
    countCloseEntityInstance = len(re.findall("\]", intent_text_commad))
    countOpenEntityType = len(re.findall("\(", intent_text_commad))
    countCloseEntityType = len(re.findall("\)", intent_text_commad))

    if countOpenEntityInstance != countCloseEntityInstance:
        return SyntaxError("Unclosed Entity Instance in line " + str(i) + ". Valid syntax [entity instance]")

    if countOpenEntityType != countCloseEntityType:
        return SyntaxError("Unclosed Entity Type in line " + str(i) + ". Valid syntax (entity_type)")

    if countOpenEntityInstance < countOpenEntityType:
        return SyntaxError("Missing an Entity Instance in line " + str(i) + ". Valid syntax [entity instance](entity_type)")

    if countOpenEntityInstance > countOpenEntityType:
        return SyntaxError("Missing an Entity Type in line " + str(i) + ". Valid syntax [entity instance](entity_type)")

    return None


def parse_markdown_content(markdown):
    cleaned_markdown = []
    #print(markdown)

    lines = re.split("[\n\r]", markdown)
    print(str(lines))
    line0 = lines[0]
    line0 = re.sub(" +", " ", line0.strip())
    cleaned_markdown.append(line0)
    if line0.startswith('## ') == False:
        raise SyntaxError("Intent Type not found in line 1. Syntax: '## intent:intent_name'")
    if valid_intent_definition(line0) == False:
        raise SyntaxError("Intent definition syntax error in line 1. Syntax: '## intent:intent_name'")

    for i in range(1, len(lines)):
        line = lines[i]
        line = re.sub(" +", " ", line.strip())
        cleaned_markdown.append(line)
        if line == '':
            continue

        is_intent_text_command = True
        is_intent_definition = True

        if line.startswith('- ') == False:
            is_intent_text_command = False

        if line.startswith('## ') == False:
            is_intent_definition = False

        if is_intent_text_command == False and is_intent_definition == False:
            raise SyntaxError("Syntax error in line " + str(i+1) + ". " + line + "  is not a text command or an intent definition.")

        if is_intent_text_command:
            is_valid = valid_intent_text_command(i+1, line)
            if is_valid != None:
                raise is_valid

        if is_intent_definition and valid_intent_definition(line) == False:
            raise SyntaxError("Intent Type not found in line " + str(i+1) + ". Syntax: '## intent:intent_name'")

    return str.join("\n", cleaned_markdown)

def parse_intent_text_command(intent_command):
    cleaned_command = ""
    cleaned_command = re.sub(" +", " ", intent_command.strip())

    if cleaned_command == '':
        raise SyntaxError("Intent text command is empty")

    is_valid = valid_intent_text_command(1, cleaned_command)
    if is_valid != None:
        raise is_valid
    return cleaned_command


