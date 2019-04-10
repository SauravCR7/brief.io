# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 12:14:14 2019

@author: Saurav
"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

from nltk.tokenize import sent_tokenize

def scrape_pdf(pdfname):

    # initial essentials
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # extract text
    f = open(pdfname, 'rb')
    for page in PDFPage.get_pages(f):
        interpreter.process_page(page)
    f.close()

    text = sio.getvalue()
    device.close()
    sio.close()

    return text

text=scrape_pdf("sample2.pdf")
text = text.replace(u'\xa0', u' ')
text = text.replace(u'\x0c', u' ')
text = text.replace(u'\n', u' ')

#text1=text.split()
#print(type(text))
print(text)