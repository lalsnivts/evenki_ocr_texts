import hfst
import configparser
import re

config = configparser.ConfigParser()
config.read('settings.ini')
transducer_morf = hfst.HfstInputStream(config['HFST']['AnalyzerFilePath']).read()


with open('dubrovskiy_aligned_28102020.csv', 'r', encoding='utf-8') as f:
    text = f.readlines()

res = open('dubrovsky_parsed.txt', 'w', encoding='utf-8')
for line in text:
    evenk = line.split('\t')[0]
    evenk = evenk.replace('- ', '')
    rus = line.split('\t')[1]
    res.write(evenk + '\n')
    res.write(rus + '\n')

    clean = re.sub('[.,~?/—";:\[\]\\\!()]', ' ', evenk)
    for i, word in enumerate(clean.split()):
        glosses = transducer_morf.lookup(word.lower())
        res.write(str(i+1) + '  ' + word + '\n')
        if len(glosses) == 0:
            res.write(str(i+1) + 'g ' + word + '\n')
        else:
            for gloss in glosses:
                res.write(str(i+1) + 'g ' + gloss[0] + '\n')
    res.write('\n')

res.close()


