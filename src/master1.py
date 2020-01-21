import os
import html
import xml.etree.ElementTree as ET
import sys
program_name = sys.argv[0]
arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]

path = arg1+'/'
the_dict = {}
for filename in os.listdir(path):
    tree = ET.parse(path+filename)
    root = tree.getroot()

    ids = []

    for child in root:
        if 'TIER_ID' in child.keys():
            if dict(child.items())['TIER_ID'] == 'fonWord':
                for ch in child:
                    for c in ch:
                        ids.append(dict(c.items())['ANNOTATION_ID'])

    morphemes = dict.fromkeys(ids)
    fons = []

    for key in morphemes.keys():
        morphemes[key] = []

    for tier in root:
        if 'TIER_ID' in tier.keys():
            if dict(tier.items())['TIER_ID'] == 'fon':
                for child in tier:
                    morphemes[dict(child[0].items())['ANNOTATION_REF']].append((child[0][0].text, dict(child[0].items())['ANNOTATION_ID']))
                    fons.append(dict(child[0].items())['ANNOTATION_ID'])

    roots = {}

    for key, value in morphemes.items():
        roots[key] = value[0]

    types = {}

    for tier in root:
        if 'TIER_ID' in tier.keys():
            if dict(tier.items())['TIER_ID'] == 'morph_type':
                for child in tier:
                    types[dict(child[0].items())['ANNOTATION_REF']] = child[0][0].text

    gls = {}
    for tier in root:
        if 'TIER_ID' in tier.keys():
            if dict(tier.items())['TIER_ID'] == 'gl':
                for child in tier:
                    if (child[0][0].text).startswith('[при.расшифровке:'):
                        w = (child[0][0].text).split('[при.расшифровке:')[1]
                        gls[dict(child[0].items())['ANNOTATION_REF']] = w                                
                    else:
                        gls[dict(child[0].items())['ANNOTATION_REF']] = child[0][0].text


    i= roots.values()
    for ii in i:
    # добавить в словарь пару (<корень,тип>=[глосса]). Если корень такого
    # типа в словаре уже есть, просто добавить глоссу в список глосс
        c_root = ii[0]
        if c_root.startswith('[при.расшифровке:'):
            c_root = c_root.split('[при.расшифровке:')[1]
        c_ind = ii[1]
        c_gls = gls[c_ind]
        try:
            c_type = types[c_ind]
        except:
            c_type = 'unkn'
        c_str = c_root+','+c_type
        if c_str not in the_dict.keys():
            the_dict[c_str] = [c_gls]
        else:
            if c_gls not in the_dict[c_str]:
                the_dict[c_str].append(c_gls) 

ww = '[оговорка],unkn'
try:
    del the_dict[ww]
    sort_list = sorted(the_dict.items(), key = lambda the_dict: the_dict[0], reverse=False)
except:
    sort_list = sorted(the_dict.items(), key = lambda the_dict: the_dict[0], reverse=False)

with open(arg3, 'w', encoding="utf-8") as t_file:
    for i in sort_list:
        t_line = i[0].split(',')[0]+'\t'+i[0].split(',')[1]+'\t'+i[1][0]
        t_file.write(t_line)
        t_file.write('\n')


with open('roots.txt', 'w', encoding="utf-8") as gl_file:
    for key, value in the_dict.items():
        if len(value) >= int(arg2):
            gl_file.write(key.split(',')[0])
            gl_file.write('\n')







