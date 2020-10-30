import configparser
import logging
import os
import re
import sys

import hfst

config = configparser.ConfigParser()
config.read('settings.ini')
transducer_morf = hfst.HfstInputStream(config['HFST']['AnalyzerFilePath']).read()

def check_params(args):
    if len(args) < 3:
        raise ValueError('Проверьте, что указали все необходимые файлы.')
    if not os.path.exists(args[1]):
        raise FileExistsError('Проверьте, что входной файл существует.')
    if not args[2].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя выходного '
                         'файла (расширение .txt)')

def parse(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as res:
        for line in text:
            evenk = line.split('\t')[0]
            evenk = evenk.replace('- ', '')
            rus = line.split('\t')[1]
            res.write(evenk + '\n')
            res.write(rus + '\n')
            clean = re.sub(r'[^\w\s-]', ' ', evenk)
            for i, word in enumerate(clean.split()):
                glosses = transducer_morf.lookup(word.lower())
                res.write(str(i + 1) + '  ' + word + '\n')
                if len(glosses) == 0:
                    res.write(str(i + 1) + 'g ' + word + '\n')
                else:
                    for gloss in glosses:
                        res.write(str(i + 1) + 'g ' + gloss[0] + '\n')
            res.write('\n')

def main():

    check_params(sys.argv)

    logging.basicConfig(filename="logfile.log", level=logging.ERROR)

    parse(sys.argv[1], sys.argv[2])
    # 'dubrovskiy_aligned.csv'
    # 'dubrovsky_parsed.txt'


if __name__ == '__main__':
    main()

