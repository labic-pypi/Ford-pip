#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from csv import reader, writer, QUOTE_MINIMAL
from os.path import basename

from .lib_input import filename_append, get_file_delimiter, time_to_print

def csv_field_length(input_name, output_name, column, maximum=None, minimum=None, encoding='utf8', quoting=QUOTE_MINIMAL):

    delimiter = get_file_delimiter(input_name)

    if not output_name:
        output_name = basename(filename_append(input_name, '_NEW'))

    int_lines_valid = 0

    with open(input_name, 'rt', encoding=encoding, errors='ignore') as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting)
        header = next(file_reader)

        try:
            column = int(column)-1 # field position (starts with 0)
        except ValueError:
            try:
                column = header.index(column) # field name
            except:
                raise RuntimeError(f'Column not found ("{column}"). Available choices: {header}.')
        
        print(f'Filtering by length (min: {minimum}, max: {maximum})...')

        with open(output_name, 'w', newline='', encoding='utf8', errors='ignore') as output_file:
            file_writer = writer(output_file, delimiter=delimiter, quoting=quoting)
            file_writer.writerow(header)
            
            for line in file_reader:
                time_to_print(file_reader.line_num)
                f_len = len(line[column])

                if str(line) != str(header)\
                and (minimum is None or f_len >= int(minimum))\
                and (maximum is None or f_len <= int(maximum)):
                    file_writer.writerow(line)
                    int_lines_valid += 1

    int_lines_total = file_reader.line_num
    int_lines_fixed = int_lines_total - int_lines_valid

    print('Read', str(int_lines_total), 'total lines.\n'+\
          str(int_lines_valid), 'lines matching length.')