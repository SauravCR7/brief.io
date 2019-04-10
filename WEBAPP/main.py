from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from flask import Flask,render_template,request,redirect, url_for,send_from_directory
import docx2txt
import os
from werkzeug import secure_filename
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from PIL import Image
import pytesseract
rsrcmgr = PDFResourceManager()
sio = StringIO()
codec = 'utf-8'
laparams = LAParams()
device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

def read_article(text):
    #file = open(file_name, "r")
    #filedata = file.readlines()
    article = text.split(". ")
    sentences = []

    for sentence in article:
        #print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    #sentences.pop() 
    
    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(text, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text and split it
    sentences =  read_article(text)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)
    #print(scores)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
    #ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    #print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(top_n):
        #print(ranked_sentence[i][1])
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    #print("Summarized Text: \n", ". ".join(summarize_text))
    return summarize_text

# let's begin
#generate_summary( "scam1.txt", 3)

UPLOAD_FOLDER = 'uploads/'

app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/summarize-text', methods=['GET','POST'])
def summarize():
    if request.method == 'POST':
        text=request.form['text']
        lines=int(request.form['lines'])
        summ=generate_summary( text, lines)
        return render_template("summary.html",text=text,summ=summ)

@app.route('/summarize-file', methods=['GET','POST'])
#def summarizefile():
 #   if request.method == 'POST':
  #      file = request.files['file']
        #print(file+'hey')
        #lines = int(request.form['lines'])
   #     if file:
    #        #print(type(file))
     #       file1=str(file)
      #      file2=file1.split(" ")
       ###   #print(file1)
          #  if file2.endswith(".docx\'"):

           #     text = docx2txt.process(file2[0]+file2[1]+file2[2]+file2[3]+file2[4]+file2[5]+file2[6]+file2[7]+file2[8])
            #    print(text)
        #text=file.read().decode("latin-1")
        #summ=generate_summary(text,lines)
        #return render_template("summary.html", text=text, summ=summ)

def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      lines = int(request.form['lines'])
      f.save(secure_filename(f.filename))
      for file in os.listdir("."):
          if file.endswith(".docx"):
              #print(f.filename)
              file=str(f.filename)
              text = docx2txt.process(file)
          elif file.endswith(".pdf"):
              rsrcmgr = PDFResourceManager()
              sio = StringIO()
              codec = 'utf-8'
              laparams = LAParams()
              device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
              interpreter = PDFPageInterpreter(rsrcmgr, device)
              f = open(f.filename, 'rb')
              for page in PDFPage.get_pages(f):
                  interpreter.process_page(page)
              f.close()

              text = sio.getvalue()
              device.close()
              sio.close()

          elif file.endswith(".jpg"):
              pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

              tessdata_dir_config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'

              # config = ('-l eng --oem 1 --psm 3')
              text = pytesseract.image_to_string(Image.open(f.filename), config=tessdata_dir_config)

      summ = generate_summary(text,lines)
      os.remove(f.filename)
      return render_template("summary.html", text=text, summ=summ)


@app.route('/' , methods=['GET','POST'])
def main():
    return render_template("form.html")

if __name__=="__main__":
    app.run(debug=True)
