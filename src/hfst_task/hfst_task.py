import hfst
import sys
import logging
import configparser
import os

def check_params(args):
    if not args[1].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя входного файла ('
                         'расширение .txt)')
    if not os.path.exists(args[1]):
        raise FileExistsError('Проверьте, что входной файл существует.')
    if not args[2].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя выходного '
                         'файла (расширение .txt)')


num = ['<sg>','<pl>']
case = ['<nom>','<acc>','<ins>','<datloc>','<locall>','<all>',
        '<prl>','<locdir>','<allprl>','<abl>','<ela>']
poss = ['<px1sg>','<px2sg>','<px3sg>','<px1pe>','<px1pi>',
        '<px2pl>','<px3pl>']

tense = ['<pres>','<nfut>','<nfut-irreg>','<past>','<past-iter>',
         '<fut>','<futcnt>','<futnear>']
person = ['<p1>', '<p2>', '<p3>']

imp = ['<imp><prox><p1><sg>','<imp><prox><p2><sg>',
       '<imp><prox><p3><sg>','<imp><prox><p1><pe>',
       '<imp><prox><p1><pi>','<imp><prox><p2><pl>',
       '<imp><prox><p3><pl>','<imp><rem><p1><sg>',
       '<imp><rem><p2><sg>','<imp><rem><p3><sg>',
       '<imp><rem><p1><pe>','<imp><rem><p1><pi>',
       '<imp><rem><p2><pl>','<imp><rem><p3><pl>']

config = configparser.ConfigParser()
config.read('settings.ini')
path = config['HFST']['BinaryFilePath']
transducer_gen = hfst.HfstInputStream(path).read()

def generate_result(input_file, result_file):
    with open(input_file, 'r', encoding='utf-8') as inp_file:
        data = inp_file.readlines()

    errors = []
    with open(result_file, 'w+', encoding='utf-8') as res_file:
        for word in data:
            list_of_wf = []
            stem = word.split()[0]
            pos = word.split()[1]
            if pos == 'n':
                for n in num:
                    for c in case:
                        for p in poss + ['']:
                            gloss = stem + '<n>' + n + c + p
                            wf = transducer_gen.lookup(gloss)
                            if wf != ():
                                list_of_wf.append(wf[0][0])
                            else:
                                errors.append(gloss)
            elif pos == 'v':
                for t in tense:
                    for p in person:
                        for n in num:
                            gloss = stem + '<v>' + t + p + n
                            wf = transducer_gen.lookup(gloss)
                            if wf != ():
                                list_of_wf.append(wf[0][0])
                            else:
                                errors.append(gloss)
                for i in imp:
                    gloss = stem + '<v>' + i
                    wf = transducer_gen.lookup(gloss)
                    if wf != ():
                        list_of_wf.append(wf[0][0])
                    else:
                        errors.append(gloss)
            for wf in set(list_of_wf):
                res_file.write(str(wf) + '\n')
            res_file.write('\n\n')

    with open('errors.txt', 'w+', encoding='utf-8') as err_file:
        for e in errors:
            err_file.write(e + '\n')

def main():
    check_params(sys.argv)

    logging.basicConfig(filename="logfile.log", level=logging.ERROR)

    input_file = sys.argv[1]
    result_file = sys.argv[2]
    generate_result(input_file, result_file)

if __name__ == '__main__':
    main()
