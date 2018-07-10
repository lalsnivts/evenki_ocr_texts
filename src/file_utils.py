#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import codecs

def read_lines_from_filename(filename):
    word_list = []
    with codecs.open(filename, 'r', 'utf-8') as fin:
        for line in fin:
            word_list.append(line.strip())
    return word_list