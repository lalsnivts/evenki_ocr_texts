#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import file_utils

PATH_IEA = 'D://Evenki//evn-xfst-latest.tar//evn-xfst-latest//evn-xfst//wordlists//evn-normalised.test'

FREQ_DEFAULT = 1

def create_evenki_wordlist():
    word_forms_freqs = collect_word_forms()
    word_stems = collect_word_stems()
    #word_forms_generated = generate_word_forms(word_stems)

def collect_word_forms():
    word_forms_freqs_iea = collect_word_forms_iea()
    return words

def collect_word_forms_iea():
    word_list = file_utils.read_lines_from_filename(PATH_IEA)
    #we don't know the real frequencies, so we'll use some default frequencies
    return {word_list_elem : FREQ_DEFAULT for word_list_elem in word_list}

def collect_word_forms_corket():
    #TODO: get from database
    return {}

def generate_word_forms(word_stems):
    pass


def collect_word_stems():
    """dict_stems = collect_word_stems_from_dictionaries()
    text_stems = collect_word_stems_from_corpora()"""


create_evenki_wordlist()