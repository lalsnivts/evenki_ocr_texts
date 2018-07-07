# coding=utf-8
__author__ = 'gisly'

import subprocess
import os
import shutil
import time
import argparse

TESSERACT_FOLDER = '/home/gisly/evenki_tesseract'
TESSDATA_FOLDER = '/home/gisly/tesseract/tesseract/'
TESSERACT_FILENAMES = ['unicharset', 'inttemp', 'normproto', 'pffmtable']

COMMAND_CREATE_IMAGE = "text2image --text=\"%(FILENAME)s\" " \
                       "--outputbase=\"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\" " \
                       "--font=%(FONT_NAME)s --fonts_dir=\"%(FONT_DIR)s\""

COMMAND_CREATE_BOX = "tesseract \"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\".tif " \
                     "\"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\" %(TESSDATA_FOLDER)s/tessdata/configs/box.train"

COMMAND_EXTRACT_UNICHAR = "unicharset_extractor %(BOX_FILES)s"
COMMAND_UNICHAR_PROPS = "set_unicharset_properties -U  \"%(TESSERACT_FOLDER)s/unicharset\" " \
                        "-O \"%(FOLDER)s/output_unicharset\" --script_dir=training/langdata"

COMMAND_MFTRAINING = "mftraining -F %(TESSERACT_FOLDER)s/font_properties -U \"%(FOLDER)s/output_unicharset\" " \
                     "-O \"%(FOLDER)s/%(LANGUAGE)s.unicharset\" %(TR_FILES)s"

COMMAND_CNTRAINING = "cntraining %(TR_FILES)s"

COMMAND_COMBINE_TESSDATA = "combine_tessdata \"%(FOLDER)s/%(LANGUAGE)s.\""

EXTENSION_TEXT = '.txt'


def process_training_data(training_folder, output_folder, language, font_name, font_dir, is_verbose):
    create_necessary_folders(output_folder, is_verbose)
    delete_existing_tesseract_files(training_folder, language)
    box_files, tr_files = process_training_files(training_folder, output_folder, language, font_name, font_dir)
    time.sleep(10)

    process_box_files(box_files, tr_files, output_folder, language, font_name, font_dir)
    time.sleep(20)

    collect_training_data(output_folder, language)


def process_training_files(training_folder, output_folder, language, font_name, font_dir):
    example_index = 0
    box_files = []
    tr_files = []
    for filename in os.listdir(training_folder):
        if is_text_file(filename):
            example_index += 1
            full_filename = os.path.join(training_folder, filename)
            box_file, tr_file = process_training_text(full_filename, output_folder,
                                                      language, font_name,
                                                      example_index, font_dir)
            box_files.append(box_file)
            tr_files.append(tr_file)

            print('=====')
            print(filename)
            if example_index > 1000:
                break

    return box_files, tr_files


def process_training_text(filename, output_folder, language, font_name, example_index, font_dir):
    command_list = [COMMAND_CREATE_IMAGE,
                    COMMAND_CREATE_BOX
                    ]

    res = process_tesseract_command_str(command_list, filename, output_folder, language, font_name, example_index,
                                        font_dir)
    print(res)

    resulting_filename = replace_properties("%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s",
                                            filename, output_folder,
                                            language, font_name, example_index, font_dir)

    box_file = resulting_filename + '.box'
    tr_file = resulting_filename + '.tr'
    return box_file, tr_file


def collect_training_data(output_folder, language):
    prepare_files(output_folder, language)
    command_list = [COMMAND_COMBINE_TESSDATA]

    res = process_tesseract_command_str(command_list, '', output_folder, language, '', 0, '')
    print(res)


def prepare_files(output_folder, language):
    copy_tesseract_files(output_folder, language)


def copy_tesseract_files(output_folder, language):
    for filename in TESSERACT_FILENAMES:
        copy_file_from_folder_to_folder(filename, TESSERACT_FOLDER, output_folder, language + '.')


# TODO: MFTRAINING???
def process_box_files(box_files, tr_files, output_folder, language, font_name, font_dir):
    box_filenames = ' '.join(['"' + box_file + '"' for box_file in box_files])
    tr_filenames = ' '.join(['"' + tr_file + '"' for tr_file in tr_files])

    command_list = [COMMAND_EXTRACT_UNICHAR,
                    COMMAND_UNICHAR_PROPS,
                    COMMAND_MFTRAINING,
                    COMMAND_CNTRAINING]

    res = ''
    try:
        res = process_tesseract_command_str(command_list, '', output_folder, language, font_name, 0,
                                            font_dir, box_filenames, tr_filenames)
    except Exception as e:
        print("Error:" + str(e))

    print(res)


def process_tesseract_command_str(command_list, filename, output_folder,
                                  language, font_name, example_index, font_dir,
                                  box_files=None, tr_files=None):
    move_to_dir = "cd " + TESSERACT_FOLDER
    command_list_tesseract = [move_to_dir] + command_list
    command_str = [replace_properties(command, filename, output_folder,
                                      language, font_name, example_index, font_dir, box_files, tr_files)
                   for command in command_list_tesseract]
    for command_str_element in command_str:
        print(command_str_element)
        res = subprocess.check_output(move_to_dir + '&' + command_str_element, shell=True).decode('cp1251')
    return res


def replace_properties(command, filename, output_folder, language,
                       font_name, example_index, font_dir,
                       box_files=None, tr_files=None):
    return command % {'FILENAME': filename,
                      'FOLDER': output_folder,
                      'LANGUAGE': language,
                      'FONT_NAME': font_name,
                      'INDEX': example_index,
                      'FONT_DIR': font_dir,
                      'TESSERACT_FOLDER': TESSERACT_FOLDER,
                      'BOX_FILES': box_files,
                      'TR_FILES': tr_files,
                      'TESSDATA_FOLDER': TESSDATA_FOLDER}


def is_text_file(filename):
    return filename.endswith(EXTENSION_TEXT)


def delete_existing_tesseract_files(folder, language_name=None):
    if language_name:
        prefix = language_name + '.'
    else:
        prefix = ''
    for filename in TESSERACT_FILENAMES:
        full_filename = os.path.join(folder, language_name + filename)
        if os.path.exists(full_filename):
            os.remove(full_filename)

    for filename in os.listdir(folder):
        if filename.startswith(prefix) and (filename.endswith('.box')
                                            or filename.endswith('.tr')
                                            or filename.endswith('.tif')):
            full_filename = os.path.join(folder, filename)
            os.remove(full_filename)

def check_folder(folder_name):
    """
    checking if a folder with a given name exists
    :param folder_name:
    :return:
    """
    if not os.path.exists(folder_name):
        raise ("Training folder %s does not exist" % folder_name)

def create_necessary_folders(folder_name, is_verbose=False):
    """
    creating folder if it does not exist
    :param folder_name:
    :param is_verbose:
    :return:
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        if is_verbose:
            print("created output folder: %s" % folder_name)

def copy_file_from_folder_to_folder(filename, from_folder, to_folder, prefix='', is_verbose=False):
    """
    copying a file from one folder to another, perhaps with a prefix
    :param filename:
    :param from_folder:
    :param to_folder:
    :param prefix:
    :param is_verbose:
    :return:
    """
    shutil.copy(os.path.join(from_folder, filename), os.path.join(to_folder, prefix + filename))
    if is_verbose:
        print('copied:%s to %s' % (os.path.join(from_folder, filename), os.path.hoin(to_folder, prefix + filename)))

def main():
    parser = argparse.ArgumentParser(description='run OCR training process')
    parser.add_argument("-i", "--input",
                        help="training folder")
    parser.add_argument("-o", "--output",
                        help="result folder")
    parser.add_argument("-l", "--language",
                        help="language")
    parser.add_argument("-fn", "--font_name",
                        help="font name")
    parser.add_argument("-ff", "--font_folder",
                        help="font folder")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output
    language = args.language
    font_name = args.font_name
    font_folder = args.font_folder
    is_verbose = args.verbose

    check_folder(input_folder)

    process_training_data(input_folder, output_folder, language, font_name, font_folder, is_verbose)

if __name__ == "__main__":
    main()

"""process_training_data('/home/gisly/evenki_tesseract/training/input',
                     '/home/gisly/evenki_tesseract/training/output',
                     'evk', 
                     'FreeMono', '/usr/share/fonts')"""
