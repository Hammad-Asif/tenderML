from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer


class LemmaTokenizer:
    ignore_tokens = [',', '.', ';', ':', '"', '``', "''",
                     '`', '!', '#', "%", '&', "'", '+', '/', '>', '<']

    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __getattribute__(self, name):
        return self[name]

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]
