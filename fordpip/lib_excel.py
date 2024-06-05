#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains the function for converting
Excel files to CSV format using python3-xlrd.
'''

from csv import writer, QUOTE_MINIMAL

try: from openpyxl import load_workbook
except: print('Warning: failed to import openpyxl.')

try: from xlrd import open_workbook
except: print('Warning: failed to import python3-xlrd.')

def csv_from_excel(input_file, output_file=None, quoting=QUOTE_MINIMAL):
    '''
    Converts excel (xls/xlsx) format files to CSV.
    '''
    if not output_file:
    	output_file = input_file.replace('xlsx','xls').replace('xls','csv')

    if output_file == input_file:
    	output_file = 'OUTPUT_' + output_file
    
    # input_xls = open_workbook(input_file)
    input_xls = load_workbook(input_file)

    output_csv = open(output_file, 'w')

    # select first sheet
    # sheet = input_xls.sheet_names()[0]
    # sheet = input_xls.sheet_by_name(sheet)
    sheet = input_xls.active

    csv_writer = writer(output_csv, quoting=quoting)

    print('Converting Excel to CSV...')

    #for line in range(sheet.nrows):
    for line in sheet.rows:
        csv_writer.writerow([cell.value for cell in line])

    output_csv.close()