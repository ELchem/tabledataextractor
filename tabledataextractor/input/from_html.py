# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_html.py

Reads an html formatted table.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""


import numpy as np
from bs4 import BeautifulSoup
import copy
import logging


# def makelist(html_table):
#     """Creates a python list from an html file"""
#     list = []
#     rows = html_table.findAll('tr')
#     for row in rows:
#         list.append([])
#         # look for rows as well as header rows
#         cols = row.findAll(["td", "th"])
#         for col in cols:
#             strings = [str(s) for s in col.findAll(text=True)]
#             text = ''.join(strings)
#             list[-1].append(text)
#     return list

def makearray(html_table):
    """Creates a numpy array from an html file"""
    n_cols = 0
    n_rows = 0

    for row in html_table.findAll("tr"):
        col_tags = row.find_all(["td", "th"])
        if len(col_tags) > 0:
            n_rows += 1
            if len(col_tags) > n_cols:
                n_cols = len(col_tags)

    array = np.full((n_rows,n_cols), fill_value=None, dtype='<U30')

    # list to store rowspan values
    skip_index = [0 for i in range(0, n_cols)]

    # iterating over each row in the table
    row_counter = 0
    for row in html_table.findAll("tr"):

        # skip row if it's empty
        if len(row.find_all(["td", "th"])) == 0:
            continue

        else:

            # get all the cells containing data in this row
            columns = row.find_all(["td", "th"])
            col_dim = []
            row_dim = []
            col_dim_counter = -1
            row_dim_counter = -1
            col_counter = -1
            this_skip_index = copy.deepcopy(skip_index)

            for col in columns:

                # determine all cell dimensions
                colspan = col.get("colspan")
                if not colspan:
                    col_dim.append(1)
                else:
                    col_dim.append(int(colspan))
                col_dim_counter += 1

                rowspan = col.get("rowspan")
                if not rowspan:
                    row_dim.append(1)
                else:
                    row_dim.append(int(rowspan))
                row_dim_counter += 1

                # adjust column counter
                if col_counter == -1:
                    col_counter = 0
                else:
                    col_counter = col_counter + col_dim[col_dim_counter - 1]

                while skip_index[col_counter] > 0:
                    col_counter += 1

                # get cell contents
                cell_data = col.get_text()

                # insert data into cell
                array[row_counter, col_counter] = cell_data

                #record column skipping index
                if row_dim[row_dim_counter] > 1:
                    this_skip_index[col_counter] = row_dim[row_dim_counter]

        # adjust row counter
        row_counter += 1

        # adjust column skipping index
        skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

    return array



# def makearray(list):
#     """Creates a numpy array from a list. Works if rows are of different length"""
#     length = len(sorted(list,key=len, reverse=True)[0])
#     array = np.array([l+[None]*(length-len(l)) for l in list],dtype=str)
#     return array


def read(file_path):
    """Method used to read an .html file and return a numpy array"""
    file = open(file_path, encoding='UTF-8')
    html_table = BeautifulSoup(file, features='lxml')
    file.close()
    #list = makelist(html_table)
    array = makearray(html_table)
    return array
