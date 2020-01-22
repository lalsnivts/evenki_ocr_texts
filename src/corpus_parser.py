import os
import xml.etree.ElementTree as ET
import sys
import logging

# corpus_parser.py eaf 1 all_words.txt


def check_params(args):
    if len(args) != 4:
        raise ValueError('Требуется 3 аргумента - имя папки, число и название файла для записи')
    if os.path.isdir(args[1]) is False:
        raise ValueError('Ошибка аргумента, проверьте название папки')
    try:
        int(args[2])
    except:
        raise ValueError('Ошибка аргумента, проверьте число глосс')
    if args[3].endswith('.txt') is False:
        raise ValueError('Ошибка аргумента, проверьте формат файла записи')


TIER_NAME_WORD = 'fonWord'
TIER_NAME_FON = 'fon'
TIER_NAME_TYPE = 'morph_type'
TIER_NAME_GL = 'gl'


def get_all_info(filename):

    tree = ET.parse(os.path.join(sys.argv[1], filename))
    root = tree.getroot()
    
    fonwords = []
    
    for i in root.findall("./TIER[@TIER_ID='%s']//REF_ANNOTATION" % TIER_NAME_WORD):
        fonwords.append(i.attrib['ANNOTATION_ID'])
        
    fons = []
    fons_ids = []
    
    for word in fonwords:
        parts = []
        parts_ids = []
        for i in root.findall("./TIER[@TIER_ID='%s']//REF_ANNOTATION[@ANNOTATION_REF='%s']" % (TIER_NAME_FON, word)):
            parts.append(i[0].text)
            parts_ids.append(i.attrib['ANNOTATION_ID'])
        fons.append(parts[0])
        fons_ids.append(parts_ids[0])
        
    types = []
    
    for fon in fons_ids:
        found = root.findall("./TIER[@TIER_ID='%s']//REF_ANNOTATION[@ANNOTATION_REF='%s']/" % (TIER_NAME_TYPE, fon))
        if found:
            types.append(str(found[0].text))
        else:
            types.append('unkn')
    
    gls = []
    
    for fon in fons_ids:
        for i in root.findall("./TIER[@TIER_ID='%s']//REF_ANNOTATION[@ANNOTATION_REF='%s']/" % (TIER_NAME_GL, fon)):
            gls.append(i.text.strip())
            
    the_dict = {}
    
    for i in range(len(fons)):
        fon_type = fons[i] + ',' + types[i]
        if fon_type not in the_dict:
            the_dict[fon_type] = set()
            the_dict[fon_type].add(gls[i])
        else:
            the_dict[fon_type].add(gls[i])
            
    return the_dict


def check(word):
    to_check = '[при.расшифровке:'
    if word.startswith(to_check):
        word = word.split(to_check)[1]
    return word


def main():

    check_params(sys.argv)

    logging.basicConfig(filename="logfile.log", level=logging.ERROR)

    the_final_dict = {}

    for filename in os.listdir(sys.argv[1]):
        try:
            for key, value in get_all_info(filename).items():
                if key not in the_final_dict:
                    key = check(key)
                    the_final_dict[key] = set()
                    the_final_dict[key].update(value)
                else:
                    the_final_dict[key].update(value)
        except Exception:
            logging.exception("Error occurred in file {}".format(filename),
                              exc_info=True)

    ww = '[оговорка],unkn'
    the_final_dict.pop(ww, None)

    with open(sys.argv[3], 'w', encoding="utf-8") as t_file:
        for word in sorted(the_final_dict):
            t_line = word.split(',')[0]+'\t'+word.split(',')[1]+'\t'+str(','.join(list(the_final_dict[word])))
            t_file.write(t_line)
            t_file.write('\n')

    with open('polysemy_roots.txt', 'w', encoding="utf-8") as gl_file:
        for key, value in the_final_dict.items():
            if len(value) > int(sys.argv[2]):
                gl_file.write(key.split(',')[0])
                gl_file.write('\n')


if __name__ == "__main__":
    main()
