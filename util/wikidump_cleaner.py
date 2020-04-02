# -*- coding: utf-8 -*-
import sys
import re
from lxml import etree
#best parameters /data/nlu/fastText/fasttext cbow -input wiki.multi.nonum.txt -output wiki_model -dim 300 -ws 8 -minn 1000 -maxn 1000 -neg 10
#Wikidump parser that parse the xml french dump of wikipedia and convert it to a txt file for Word Representation learning
def clean_wiki_text(text):

    cleaned_text = []
    if text == None:
        return ""

    for line in text.split("\n"):

        """For each line between <text> and </text> filter elements not a text content"""
        is_text_content = True

        if re.match("^\[\[[a-z]{2,3}:.+\]\]$", line, re.IGNORECASE) != None:  # check if the line is a link for another language
            is_text_content = False
        if re.match("^#REDIRECT .+$", line, re.IGNORECASE) != None:  # check if the line is a redirection
            is_text_content = False
        if re.match("^<.+>$",line) != None: #check if the line is an xml element
            is_text_content = False
        if re.match("^\{\| ?class.+$", line) != None: #check if the line is a table start element
            is_text_content = False
        if re.match("^ ?\|.*$", line) != None: #check if the line is a table or infobox element
            is_text_content = False
        if re.match("^\|\}$", line) != None: #check if the line is a table end element
            is_text_content = False
        if re.match("^! ?[^=]+$", line) != None: #check if the line is a table element ! Notation ! Type
            is_text_content = False
        if re.match("^\{\{ ?infobox.*$", line, re.IGNORECASE) != None: #check if the line is an infobox element
            is_text_content = False
        if re.match("^\}\}$", line) != None: #check if the line is an infobox end element
            is_text_content = False

        if is_text_content == True:
            line = re.sub("\{\{Légende/(Début|Fin)\}\}","", line, re.IGNORECASE) # remove legende start and legend end
            line = re.sub("^=+ ?([^=]+) ?=+$","\g<1>", line, re.IGNORECASE) #remove === === OR == == from title
            line = re.sub("([a-z]+ ?= ?)?(www\.|https:|http:)[^\s]+", "", line, re.IGNORECASE)  # delete url link and conserve text link
            line = re.sub("<[^ ]+>","", line) #delete xml element from text
            line = re.sub("\|thumb", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|left", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|right", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|center", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|\d+px", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|vignette", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|redresse", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|gauche", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|droite", "", line, re.IGNORECASE)  # remove image tag
            line = re.sub("\|légende\|#[a-z0-9]+\|","", line, re.IGNORECASE) # remove image legend légende|#e1c44a|
            #line = re.sub("\[\[[^:]+:(.+)\]\]", "[[\g<1>]]", line) #delete data type [[category:....]] [[file:...]]
            #line = re.sub("\{\{[^:]+:(.+)\}\}","{{\g<1>}}", line) #delete data type {{default:....}} {{image:...}}
            line = re.sub("\[\[[a-zA-Z0-9]+:([^\|\]\.]+)(\.[a-z]{1,4})?(\||\])", "[[\g<1>\g<3>", line)  # delete data type [[category:....]] [[file:...]] and file extension
            line = re.sub("\{\{[a-zA-Z0-9]+:([^\|\}\.]+)(\.[a-z]{1,4})?(\||\})", "{{\g<1>\g<3>", line)  # delete data type {{default:....}} {{image:...}} and file extension
            line = re.sub("\[\[[a-zA-Z0-9 ]+#([^\|\]\.]+)(\.[a-z]{1,4})?(\||\])", "[[\g<1>\g<3>", line)  # delete data type [[category:....]] [[file:...]] and file extension
            line = re.sub("\{\{[a-zA-Z0-9 ]+#([^\|\}\.]+)(\.[a-z]{1,4})?(\||\})", "{{\g<1>\g<3>", line)  # delete data type {{default:....}} {{image:...}} and file extension

            line = re.sub("(langue|lang)\|[a-z]{2,3}\|","", line, re.IGNORECASE) #delete language element
            line = re.sub("\|(langue|lang)=[a-z]{2,3}", "", line, re.IGNORECASE) #delete language element
            line = re.sub("\{\{ ?lien ?(web|arxiv)? ?\|", "{{", line, re.IGNORECASE) #delete link (lien, lien web) element
            line = re.sub("\{\{ ?citation ?\|(.+)\}\}", " \g<1> ", line, re.IGNORECASE) #Normalise citation template
            line = re.sub("\|\s?\|", "|", line)
            line = re.sub("['’ʾ′ˊˈꞌ‘ʿ‵ˋ'’ʼʻʽʾʿˈ՚‘‚‛,`´′ʹ‵Ꞌꞌ]+"," ", line) #delete quote
            #line = re.sub("[']{2,}", "'", line) #delete multiple quote
            #line = re.sub("^'|(\s+'|'\s+)|'$", " ", line) #delete useless quote
            line = re.sub("(\*\*| \*|\* )"," ", line) #delete bold tag
            line = re.sub("(__| _|_ )", " ", line)  # delete underline tag
            line = re.sub("\s+", " ", line) #delete multiple space
            line = re.sub("[\| ]{2,}", "|", line) # delete multiple pipe
            line = re.sub("\- ?(\[ \]|\[x\]|\[X\])", "", line) #delete checked and not checked box
            line = re.sub("[0-9]", " ", line) #delete number
            line = line.strip()


            line = clean_template(line) #format to plain text template element {{date|1|12|2015}} -> 1-12-2015 [[file:algorithm.pdf|algorithm theory]] -> algorithm theory
            #line = line.lower()
            #line = re.sub("[^a-záàâäãåçéèêëíìîïñóòôöõúùûüæœâêôûéàèùÿàâçéèêëîíïôûùüÿñæœ0-9\-]"," ", line)
            line = re.sub("\B-\B|^-|-$|- | -"," ", line) #delete not text included dash -
            line = re.sub("[^0-9a-zA-ZÄÅÇÉÑÖÜÃÕŒÆŸÂÊÁËÈÍÎÏÌÓÔÒÚÛÙáàâäãåçéèêëíìîïñóòôöõúùûüæœâêôûéàèùÿàâçéèêëîíïôûùüÿñæœ\-]", " ", line)
            #print (line)

            line = re.sub("\s+", " ", line)
            line = line.strip()
            cleaned_text.append(line)

    #print(" ".join(cleaned_text))

    if len(cleaned_text) > 0:
        return " ".join(cleaned_text)
    else:
        return ""

def clean_template(line):
    loop = 0
    while(re.match(".*\[\[([^\]\[]+)\]\].*", line) != None or re.match(".*\{\{([^\}\{]+)\}\}.*", line) !=None) and loop <= 5:
        line = clean_curly_bracket_template(line)
        line = clean_square_bracket_template(line)
        loop = loop + 1 #to avoid an infinite loop
    return line


def clean_curly_bracket_template(line):
    template_iterator = re.finditer("\{\{([^\}\{]+)\}\}", line)
    str_replacement = {}

    for element in template_iterator:
        template = element.group(0)
        value = element.group(1)
        size = len(value)
        list = []
        param = ""
        open_close_bracket = 0
        for i, c in enumerate(value):
            if c == "[":
                open_close_bracket = open_close_bracket + 1
            if c == "]":
                open_close_bracket = open_close_bracket - 1
            if c != "|" or open_close_bracket != 0:
                param = param + c
            if (c == "|" and open_close_bracket == 0) or i == size - 1:
                list.append(param.strip())
                param = ""

        if len(list) == 1:
            str_replacement[template] = re.sub(" ", "-", list[0].strip())
        else:
            filtered_list = []
            for list_element in list[1:]:
                if re.match("^[a-z]+ ?=.+$", list_element, re.IGNORECASE) == None:
                    filtered_list.append(list_element)
            str_replacement[template] = re.sub(" ", "-", " ".join(filtered_list).strip())
    #print(str_replacement)
    for key in sorted(str_replacement, key=len, reverse=True):
        #print(key + " >> " + str_replacement[key])
        try:
            line = re.sub(re.escape(key), str_replacement[key], line)
        except:
            print ('Error in clean_curly_bracket_template() with ' + line)

    return line

def clean_square_bracket_template(line):
    template_iterator = re.finditer("\[\[([^\]\[]+)\]\]", line)
    str_replacement = {}
    for element in template_iterator:
        template = element.group(0)
        value = element.group(1)
        size = len(value)
        list = []
        param = ""
        open_close_bracket = 0
        for i, c in enumerate(value):
            if c == "{":
                open_close_bracket = open_close_bracket + 1
            if c == "}":
                open_close_bracket = open_close_bracket - 1
            if c != "|" or open_close_bracket != 0:
                param = param + c
            if (c == "|" and open_close_bracket == 0) or i == size - 1:
                list.append(param.strip())
                param = ""

        if len(list) == 1:
            str_replacement[template] = re.sub(" ", "-", list[0].strip())
        else:
            filtered_list = []
            for list_element in list[1:]:
                if re.match("^[a-z]+ ?=.+$", list_element, re.IGNORECASE) == None:
                    filtered_list.append(list_element)
            str_replacement[template] = re.sub(" ", "-", " ".join(filtered_list).strip())
    for key in sorted(str_replacement, key=len, reverse=True):
        #print(key + " >> " + str_replacement[key])
        try:
            line = re.sub(re.escape(key), str_replacement[key], line)
        except:
            print ('Error in clean_square_bracket_template() with ' + line)

    return line

if __name__ == '__main__':
    wiki_dump_path = sys.argv[1]
    output_path = sys.argv[2]

    #wiki_dump_path = 'frwiki-20101103-pages-articles-sample.xml'
    #wiki_dump_path = 'wiki.xml'
    #output_path = 'result.txt'
    output_file = open(output_path, "w+")
    output_file_lower = open(output_path + ".lower", "w+")
    xmlns = ""
    with open(wiki_dump_path, 'r') as fp:
        line = fp.readline()
        xmlns = re.search(" xmlns=\"([^\"]+)\"",line)
        xmlns = xmlns.group(1)
        print("File name space: " + xmlns)
    fp.close()


    with open(wiki_dump_path, 'rb') as fp:
        elements = etree.iterparse(fp, tag = "{"+xmlns+"}text", encoding="utf-8")
        for event, element in elements:
            wiki_text = clean_wiki_text(element.text)
            wiki_text = re.sub("\B\-+\B|^\-+|\-+$|\-+ | \-+", " ", wiki_text)  # delete not text included dash -
            wiki_text = re.sub("\s+", " ", wiki_text)
            wiki_text = wiki_text.strip()
            #print(wiki_text)
            output_file.write(wiki_text + " ")
            output_file_lower.write(wiki_text.lower() + " ")
            element.clear()


    fp.close()
    output_file.close()
    output_file_lower.close()


