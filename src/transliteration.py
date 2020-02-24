import sys
import logging

# python transliteration.py all_words.txt 0

vowels = {'а̄':'ā', 'ō':'ō', 'ē':'ē', 'ū':'ū', 'ī':'ī', 'ə̄':'ə', 'ә̄':'ə'}

equiv = {'a':'а', '\'':'ь', '’':'ь', 'b':'б', 'v':'в', 'g':'г', 'd':'д',
         'k':'к', 'l':'л', 'm':'м', 'n':'н', 'p':'п', 'r':'р', 's':'с',
         't':'т', 'c':'ц', 'f':'ф', 'x':'х', 'h':'х', 'γ':'г', 'š':'ш',
         'w':'в', 'i':'и', 'j':'й', 'ŋ':'нг', 'č':'ч', 'ž':'ж', 'ǯ':'з',
         'y':'ы', 'o':'о', 'u':'у', 'e':'е', 'ď':'дь', 'ə':'э', 'ā':'ā',
         'ō':'ō', 'ɨ':'ы', 'ū':'ӯ', 'ī':'ӣ', 'ε':'ε', 'ń':'нь',
         'ś':'сь', 'í':'и', 'z':'з', 'ē':'ē', 'ә':'э', 'ō':'ō',
         '́':'', 'ɔ':'о', 'ť':'ть', '̅':'', 'а':'а'}

pairs = {'шь':'щ', 'ьа':'я', 'ьо':'ё', 'ьэ':'е', 'ьу':'ю', 'ьы':'и',
         'ьи':'и', 'ье':'е', 'йу':'ю', 'йо':'ё', 'йэ':'е',
         'йа':'я', 'тс':'ц', 'йы':'и', 'йā':'я̄', 'ьā':'я̄', 'йō':'ё',
         'ьō':'ё', 'йӯ':'ю̄', 'ьӯ':'ю̄', 'йē':'ē', 'ьē':'ē'}


def check_params(args):
    if not args[1].endswith('.txt'):
        raise ValueError('Проверьте, что ввели корректное имя файла (расширение .txt)')
    if args[2] != '0' and args[2] != '1':
        raise ValueError('Проверьте заданное направление транслитерации (0 '
                         'или 1)')


def transliteration(word: str) -> str:
    for key in vowels.keys():
        word = word.replace(key, vowels[key])
    if word.startswith('e'):
        word = 'ә' + word[1:]
    for key in equiv.keys():
        word = word.replace(key, equiv[key])
    for key in pairs.keys():
        word = word.replace(key, pairs[key])
    return word


def realisation(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.readlines()
    with open('dict_cyrillic.txt', 'w', encoding='utf-8') as g:
        for line in text:
            new_line = transliteration(line.split()[0].lower().strip('[]…'))\
                       + '\t' + '\t'.join(line.split()[1:]) + '\n'
            g.write(new_line)


def main():
    check_params(sys.argv)

    logging.basicConfig(filename="logfile.log", level=logging.ERROR)

    if sys.argv[2] == '0':
        realisation(sys.argv[1])


if __name__ == '__main__':
    main()
