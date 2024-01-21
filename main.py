from fileinput import filename
from flask import Flask, request, jsonify
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from createCSV import createCSVFile
from model import Classifier
import traceback
import nltk
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import sys
import gc
import pickle
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

app = Flask(__name__)
token = "tenderML"


class LemmaTokenizer:
    ignore_tokens = [',', '.', ';', ':', '"', '``', "''",
                     '`', '!', '#', "%", '&', "'", '+', '/', '>', '<']

    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]


def deleteFiles(fileName):
    if os.path.exists("./PdfFile/"+fileName):
        os.remove("./PdfFile/"+fileName)
    # if os.path.exists("csvFile/"+fileName+".csv"):
    #     os.remove("csvFile/"+fileName+".csv")


@app.route("/classifyData", methods=['POST'])
def run():
    try:
        if request.headers.get('Authorization') != token:
            return "Unauthorized User"
        pdf = request.files['file']
        fileName = secure_filename(pdf.filename)
        pdf.save('./PdfFile/'+secure_filename(pdf.filename))
        # df = createCSVFile(fileName)
        # df.to_csv(fileName+".csv", encoding='utf-8-sig')
        # crf = pickle.load(open("./models/crf.pk", 'rb'))
        SVM_Model = pickle.load(open("./models/SVM.pk", 'rb'))
        vectorizer = pickle.load(open("./models/vectorizer.pk", "rb"))
        cls = Classifier(SVM_Model, vectorizer)
        frame = [cls.classify('PdfFile/'+fileName)]
        del(pdf)
        del(cls)
        del(SVM_Model)
        del(vectorizer)
        gc.collect()
        deleteFiles(fileName)
    except Exception as e:
        deleteFiles(fileName)
        return traceback.format_exc()
    return jsonify(frame.pop(0))


if __name__ == "__main__":
    app.run(debug=True)
