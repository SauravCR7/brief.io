# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 15:20:51 2019

@author: Saurav
"""
import language_check
from PIL import Image
import cv2
import pytesseract
from textblob import TextBlob

tool = language_check.LanguageTool('en-UK')

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'


#config = ('-l eng --oem 1 --psm 3')
text = pytesseract.image_to_string(Image.open('ultimate_scam2.jpg'),config=tessdata_dir_config)
print(text)

print("####################################################################################")

matches = tool.check(text)
correct_text=language_check.correct(text, matches)
text=' '.join(correct_text.split())
text = TextBlob(text)

#print(type(text))
print(text)