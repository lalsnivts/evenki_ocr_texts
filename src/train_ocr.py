#!/usr/bin/python3
# coding=utf-8
__author__ = 'gisly'

import subprocess
import os
import shutil
import time
import argparse
import logging

# TESSERACT_FOLDER = '/home/gisly/evenki_tesseract'
# TESSDATA_FOLDER = '/home/gisly/tesseract-ocr/tessdata/tesseract/'

TESSERACT_FILENAMES = ['unicharset', 'inttemp', 'normproto', 'pffmtable']

COMMAND_CREATE_IMAGE = "text2image --text=\"%(FILENAME)s\" " \
                       "--outputbase=\"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\" " \
                       "--font=%(FONT_NAME)s --fonts_dir=\"%(FONT_DIR)s\""

COMMAND_CREATE_BOX = "tesseract \"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\".tif " \
                     "\"%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s\" %(TESSDATA_FOLDER)s/configs/box.train"

COMMAND_EXTRACT_UNICHAR = "unicharset_extractor %(BOX_FILES)s"
COMMAND_UNICHAR_PROPS = "set_unicharset_properties -U  \"%(TESSERACT_FOLDER)s/unicharset\" " \
                        "-O \"%(FOLDER)s/output_unicharset\" --script_dir=training/langdata"

COMMAND_MFTRAINING = "mftraining -F %(TESSERACT_FOLDER)s/font_properties -U \"%(FOLDER)s/output_unicharset\" " \
                     "-O \"%(TESSERACT_FOLDER)s/%(LANGUAGE)s.unicharset\" %(TR_FILES)s"

COMMAND_CNTRAINING = "cntraining %(TR_FILES)s"

COMMAND_COMBINE_TESSDATA = "combine_tessdata \"%(LANGUAGE)s.\""

EXTENSION_TEXT = '.txt'

MODE_TRAIN_ONLY = 1
MODE_BOX_ONLY = 2
MODE_ALL = 3


def process_training_data(training_folder, output_folder, language, font_name, font_dir, tessdata_folder,
                          mode,
                          is_verbose=False):
    create_necessary_folders(output_folder, is_verbose)
    if mode != MODE_TRAIN_ONLY:
        # delete_existing_tesseract_files(training_folder, language, is_verbose)
        box_files, tr_files = process_training_files(training_folder, output_folder,
                                                     language, font_name, font_dir, tessdata_folder, is_verbose)

    if mode != MODE_BOX_ONLY:
        process_box_files(training_folder, box_files, tr_files, output_folder, language, font_name, font_dir,
                          tessdata_folder, is_verbose)
        time.sleep(20)

    collect_training_data(training_folder, output_folder, language, is_verbose)


def process_training_files(training_folder, output_folder, language,
                           font_name, font_dir, tessdata_folder,
                           is_verbose=False):
    example_index = 0
    box_files = []
    tr_files = []
    for filename in os.listdir(training_folder):
        if is_text_file(filename):
            example_index += 1
            full_filename = os.path.join(training_folder, filename)
            if is_verbose:
                logging.info("Starting to process %s (%s)" % (full_filename, example_index))
            box_file, tr_file = process_training_text(training_folder,
                                                      full_filename, output_folder,
                                                      language, font_name,
                                                      example_index, font_dir, tessdata_folder,
                                                      is_verbose)
            box_files.append(box_file)
            tr_files.append(tr_file)

            if example_index % 100 == 0:
                logging.info("Processed training file %s" % example_index)

    return box_files, tr_files


def process_training_text(training_folder, filename, output_folder, language,
                          font_name, example_index, font_dir,
                          tessdata_folder, is_verbose):
    command_list = [COMMAND_CREATE_IMAGE,
                    COMMAND_CREATE_BOX
                    ]

    res = process_tesseract_command_str(training_folder, command_list, filename, output_folder, language,
                                        font_name, example_index,
                                        font_dir, tessdata_folder, is_verbose=is_verbose)
    if is_verbose:
        logging.info("process_training_text:%s" % res)

    resulting_filename = replace_properties("%(FOLDER)s/%(LANGUAGE)s.%(FONT_NAME)s.exp%(INDEX)s",
                                            filename, training_folder,
                                            output_folder,
                                            language, font_name, example_index,
                                            font_dir, tessdata_folder)

    box_file = resulting_filename + '.box'
    tr_file = resulting_filename + '.tr'
    return box_file, tr_file


def collect_training_data(training_folder, output_folder, language, is_verbose=False):
    previous_dir = os.getcwd()
    try:
        prepare_files(output_folder, language)
        os.chdir(os.path.join(output_folder, language))
        command_list = [COMMAND_COMBINE_TESSDATA]

        res = process_tesseract_command_str(training_folder,
                                            command_list, '', output_folder, language, '', 0, '',
                                            tessdata_folder='',
                                            box_files=None,
                                            is_verbose=is_verbose)
        logging.info("collect_training_data:%s", res)
    finally:
        os.chdir(previous_dir)


def prepare_files(output_folder, language):
    copy_tesseract_files(output_folder, language)


def copy_tesseract_files(output_folder, language):
    output_language_folder = create_necessary_folders(os.path.join(output_folder, language))
    for filename in TESSERACT_FILENAMES:
        copy_file_from_folder_to_folder(filename, './', output_language_folder, language + '.')


# TODO: MFTRAINING???
def process_box_files(training_folder,
                      box_files, tr_files, output_folder, language, font_name, font_dir, tessdata_folder,
                      is_verbose=False):
    box_filenames = ' '.join(['"' + box_file + '"' for box_file in box_files])
    tr_filenames = ' '.join(['"' + tr_file + '"' for tr_file in tr_files])

    command_list = [COMMAND_EXTRACT_UNICHAR,
                    COMMAND_UNICHAR_PROPS,
                    COMMAND_MFTRAINING,
                    COMMAND_CNTRAINING]

    res = 'no result'
    try:
        res = process_tesseract_command_str(training_folder,
                                            command_list, '', output_folder, language, font_name, 0,
                                            font_dir, tessdata_folder,
                                            box_filenames, tr_filenames,
                                            is_verbose=is_verbose)
    except Exception as e:
        logging.error("Error processing process_box_files:" + str(e))

    if is_verbose:
        logging.info("process_box_files: %s" % res)


def process_tesseract_command_str(training_folder, command_list, filename, output_folder,
                                  language, font_name, example_index, font_dir,
                                  tessdata_folder,
                                  box_files=None, tr_files=None,
                                  is_verbose=False):
    move_to_dir = "cd " + output_folder
    command_list_tesseract = [move_to_dir] + command_list
    command_str = [replace_properties(command, filename, training_folder,
                                      output_folder,
                                      language, font_name, example_index, font_dir,
                                      tessdata_folder,
                                      box_files, tr_files)
                   for command in command_list_tesseract]
    for command_str_element in command_str:
        if is_verbose:
            logging.info("process_tesseract_command_str: %s" % command_str_element)
        res = subprocess.check_output(move_to_dir + '&' + command_str_element, shell=True,
                                      stderr=subprocess.STDOUT).decode('utf-8')
    return res


def replace_properties(command, filename,
                       training_folder, output_folder, language,
                       font_name, example_index, font_dir,
                       tessdata_folder,
                       box_files=None, tr_files=None):
    return command % {'FILENAME': filename,
                      'FOLDER': output_folder,
                      'LANGUAGE': language,
                      'FONT_NAME': font_name,
                      'INDEX': example_index,
                      'FONT_DIR': font_dir,
                      'TESSERACT_FOLDER': training_folder,
                      'BOX_FILES': box_files,
                      'TR_FILES': tr_files,
                      'TESSDATA_FOLDER': tessdata_folder}


def is_text_file(filename):
    return filename.endswith(EXTENSION_TEXT)


def delete_existing_tesseract_files(folder, language_name=None, is_verbose=False):
    if language_name:
        prefix = language_name + '.'
    else:
        prefix = ''
    for filename in TESSERACT_FILENAMES:
        full_filename = os.path.join(folder, language_name + filename)
        if os.path.exists(full_filename):
            os.remove(full_filename)
            if is_verbose:
                logging.info("Removing folder %s " % full_filename)

    for filename in os.listdir(folder):
        if filename.startswith(prefix) and is_generated_file(filename):
            full_filename = os.path.join(folder, filename)
            os.remove(full_filename)
            logging.info("Removing folder %s " % full_filename)


def check_file_exists(filename):
    """
    checking if a file with a given name exists
    :param filename:
    :return:
    """
    if not os.path.exists(filename):
        raise Exception("File %s does not exist" % filename)


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
            logging.info("created output folder: %s" % folder_name)
    return folder_name


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
        logging.info(
            'copied:%s to %s' % (os.path.join(from_folder, filename), os.path.hoin(to_folder, prefix + filename)))


def is_generated_file(filename):
    return filename.endswith('.box') or filename.endswith('.tr') or filename.endswith('.tif')


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(description='run OCR training process')
    parser.add_argument("input",
                        help="training folder")
    parser.add_argument("output",
                        help="result folder")
    parser.add_argument("language",
                        help="language")
    parser.add_argument("font_name",
                        help="font name")
    parser.add_argument("font_folder",
                        help="font folder")
    parser.add_argument("tessdata_folder",
                        help="tessdata folder")
    parser.add_argument("mode",
                        help="mode: 1 to generate box files, 2 to train, 3 to generate and combine")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output
    language = args.language
    font_name = args.font_name
    font_folder = args.font_folder
    tessdata_folder = args.tessdata_folder
    mode = args.mode
    is_verbose = args.verbose

    check_file_exists(input_folder)
    check_file_exists(tessdata_folder)
    check_file_exists(os.path.join(input_folder, "font_properties"))

    process_training_data(input_folder, output_folder, language, font_name, font_folder, tessdata_folder,
                          mode,
                          is_verbose)


if __name__ == "__main__":
    main()

"""process_training_data('/home/gisly/evenki_tesseract/training/input',
                     '/home/gisly/evenki_tesseract/training/output',
                     'evk', 
                     'FreeMono', '/usr/share/fonts')"""
