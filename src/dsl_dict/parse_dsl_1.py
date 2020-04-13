import sys
import logging
import os
import re
import pymystem3
import json
from datetime import datetime
from itertools import islice

MAX_NUM = 15000


def check_params(args):
    if len(args) < 3:
        raise ValueError('Проверьте, что указали все необходимые файлы.')
    if not args[1].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя входного файла ('
                         'расширение .txt)')
    if not os.path.exists(args[1]):
        raise FileExistsError('Проверьте, что входной файл существует.')
    if not args[2].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя выходного '
                         'файла (расширение .txt)')


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def files(input_dict):
    with open('short.txt', 'r', encoding='utf-8') as f:
        file = f.read().split('\n\n')

    short = file[0].split('\n')
    dialect = file[1].split('\n')

    with open(input_dict, 'r', encoding='utf-8') as g:
        dsl_dict = g.readlines()

    return dsl_dict, short, dialect


def detect_pos(m, string):
    data = json.dumps(m.analyze(string), ensure_ascii=False)
    data = json.loads(data)
    pos_l = []
    for i in range(0, len(data), 2):
        try:
            pos = data[i]['analysis'][0]['gr']
            if pos.startswith('V'):
                pos_l.append('v')
            elif pos.startswith('S'):
                pos_l.append('n')
            elif pos.startswith('A'):
                pos_l.append('adj')
            elif pos.startswith('PART'):
                pos_l.append('ij')
        except:
            pos_l.append('unkn')

    return pos_l


def parsing(BATCH_SIZE, dsl_dict, short, dialect):

    m = pymystem3.Mystem()

    idx_word = []
    words = []
    infos = []
    pos_list = []
    for i in range(3, 60001):
        s = dsl_dict[i]
        if not s.startswith('\t'):
            idx_word.append(i)
            words.append(s.strip())

    for l in range(len(short) - 2):
        if short[l] == 'см.':
            del short[l]
        if short[l] == 'что-л.':
            del short[l]

    print('Кол-во слов:', len(words))
    for q in range(len(idx_word)-1):

        if q % 100 == 0:
            print(q, datetime.now())

        if q == MAX_NUM:
            break

        s = ' '.join([w.strip() for w in dsl_dict[idx_word[q]+1:idx_word[q+1]]])
        if s is None:
            s = ''
        re_search = re.search('\[.*?\].*?\[.*?\](.*?)\[.*?\]', s)
        if re_search is None:
            continue
        s = re_search.group(1)
        s_list = s.split(' ')
        start = 0
        end = 0
        st_ch = 0
        if '2)' and '2.' not in s_list:
            for i in range(len(s_list)-1):
                for d in dialect:
                    if s_list[i].startswith(d):
                        start = i
                        st_ch = 1
                for l in short:
                    if s_list[i].startswith(l):
                        start = i
                        st_ch = 1
            if 'см.' in s_list:
                end = s_list.index('см.')
        if '2)' in s_list or '2.' in s_list:
            try:
                end = s_list.index('2)')
            except:
                end = s_list.index('2.')
            for i in range(end-1):
                for d in dialect:
                    if s_list[i].startswith(d):
                        start = i
                        st_ch = 1
                for l in short:
                    if s_list[i].startswith(l):
                        start = i
                        st_ch = 1
            if 'см.' in s_list:
                if end > s_list.index('см.'):
                    end = s_list.index('см.')

        result = []

        if start == 0 and st_ch == 0:
            start = -1
        if end != 0:
            if start > end:
                start = -1
            for i in range(start+1, end):
                result.append(s_list[i])
        else:
            for i in range(start+1, len(s_list)-1):
                result.append(s_list[i])

        for r in result:
            if r.endswith(')'):
                result = result[result.index(r)+1:]

        info = ' '.join(result)
        info = info.split(';')[0]
        if info.startswith('3 '):
            info = info.split('3 ')[1]
        if info.startswith('1.'):
            info = info.split('1.')[1]
        if info.endswith('.'):
            info = info.split('.')[0]

        infos.append(re.split('[-\s\(\),\.\?̄\'!]', info.strip())[0])

        if 'межд.' in s_list:
            pos = 'ij'
        else:
            if words[len(infos)-1].endswith('-мӣ'):
                pos = 'v'
            else:
                pos = "nothing"
        pos_list.append(pos)

    final_list = []
    work_list = []
    for j in range(len(pos_list)-1):
        if pos_list[j] == "nothing":
            work_list.append(j)
    work_list = list(chunk(work_list, BATCH_SIZE))
    for el_index, el in enumerate(work_list):
        text = []
        for q in el:
            text.append(infos[q].split(' ')[0])
        text_joined = ' '.join(text)
        pos_l = detect_pos(m, text_joined)
        print(el_index, text_joined, pos_l, len(el), len(pos_l))
        for p in range(len(pos_l)):
            pos_list[el[p]] = pos_l[p]

    print('pos_processed', datetime.now())

    print(len(words), len(infos), len(pos_list))
    for i in range(0, min(len(words)-1, MAX_NUM)):
        final_list.append(words[i] + '\t' + infos[i] + '\t' + pos_list[i])


    return final_list


def saving(final_list, filename):
    with open(filename, 'w+', encoding='utf-8') as f:
        for s in final_list:
            f.write(s + '\n')


def main():

    BATCH_SIZE = 500

    check_params(sys.argv)

    logging.basicConfig(filename="logfile.log", level=logging.ERROR)

    dsl_dict, short, dialect = files(sys.argv[1])
    saving(parsing(BATCH_SIZE, dsl_dict, short, dialect), sys.argv[2])


if __name__ == '__main__':
    main()
