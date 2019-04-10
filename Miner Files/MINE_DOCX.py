# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 13:55:49 2019

@author: Saurav
"""

import docx2txt

def scrape_docx(docx):

    text = docx2txt.process(docx)

    return text

t=scrape_docx("sample1.docx")
print(t)