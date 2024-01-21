import encodings
from numpy import isnan
import re
import pandas as pd
import pdfplumber
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import sklearn_crfsuite
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import pickle
from sklearn import model_selection, svm
import nltk
import json
from joblib import load
import gc
import tree
import unicodedata


class Classifier:
    def __init__(self, svm, vectorizer):
        self.SVM_Model = svm
        self.vectorizer = vectorizer
        units = ['h', 'm²Wo', 'mWo', 'cm', 'to', 'sqft','Satz' 'Mt', 'qm', 'cbm', 'lfdm', 'Stk', 'St', 'PA', 'd', 'Monat', 'Jahre', 'ldm', 'pauschal', 'Stück',
                 'Stck', 'Psch', 'Psh', 'm[23]', 'Pau', 'm', 'mm', 'm²', 'm³', 'Std.', 'Std', 'psh.', 'lfm', 'Wo', 'm2Wo', 'StWo', 't', 'Mon', 'kg', 'Woche']
        self.unitsOnly = "("
        for un in units:
            self.unitsOnly += "("+un+")\\b|"+"(" + \
                un.upper()+")\\b|"+"("+un.lower()+")\\b|"
        self.unitsOnly = self.unitsOnly[:-1]
        self.unitsOnly += ")"
        self.onlyUnits = "("
        for un in units:
            self.onlyUnits += "\\b("+un+")\\b|"+"\\b(" + \
                un.upper()+")\\b|"+"\\b("+un.lower()+")\\b|"
        self.onlyUnits = self.onlyUnits[:-1]
        self.onlyUnits += ")"
        self.unitsRegx = "([0-9]+(\.|\,)*)+(\ )*"+self.unitsOnly
        self.bulletRegex = "((Titel(\s)*)|(Kapitel(\s)*)|(Abschnitt(\s)*)|(LB(\s)*)|(Gewerk(\s)*))?([0-9]+(\.)*(\ )?)+[0-9]*"
        self.spaceBulletRegex = "([0-9]+(\ ){1,3})+([A-Z]{0,1}\\b)"
        self.date = "[0-9]{1,2}\.[0-9]{1,2}\.([1][9]|[2][0])[0-9]{2}"

    def __del__(self):
        print("deleting......")
        del(self.SVM_Model)
        del(self.vectorizer)
        del(self.unitsRegx)
        del(self.bulletRegex)
        del(self.unitsOnly)
        del(self.date)
        gc.collect()

    def read_File(self, fileName):
        reader = pdfplumber.open(fileName)
        pages = reader.pages
        text = []
        for id, pg in enumerate(pages):
            txt = pg.extract_text(layout=True).split('\n')
            txt = [{'Text': x.strip(), 'Page': id+1}
                   for x in txt if x.strip() != '']
            text.extend(txt)
        df = pd.DataFrame(text)
        reader.close()
        return df

    def findSeq(self, lst):
        zSeq = []
        zSeq_push = zSeq.append
        i = 0
        while i < len(lst):
            d = lst[i]
            s = []
            s_push = s.append
            s = [d]
            while i < len(lst)-1 and d+1 == lst[i+1]:
                i += 1
                d = lst[i]
                s_push(d)
            else:
                i += 1
            zSeq_push(s)
        zSeq = tuple(x for x in zSeq if len(x) > 2)
        zSeq = tuple(x for y in zSeq for x in y)
        return zSeq

    def labelCorrection(self, df):
        df = df.copy(deep=True)
        zero = tuple(i for i, r in enumerate(df['labels'].to_list()) if r == 0)
        zero = self.findSeq(zero)
        if len(zero) > 0:
            for a, row in df.iterrows():
                if a not in zero:
                    if row['labels'] == 1 and row['probability'] < 0.90:
                        df.loc[a, 'labels'] = 0
                if a == max(zero):
                    break
        ons = tuple(i for i, r in enumerate(df['labels'].to_list()) if r == 1)
        ons = sorted(self.findSeq(ons))
        if len(ons) > 0:
            if len(ons) > 2:
                for id, k in enumerate(ons):
                    if id != 0:
                        if k-ons[id-1] <= 3:
                            ons = ons[id:]
                            break
            for a, row in df.iterrows():
                if a >= min(ons):
                    if a not in ons:
                        if row['labels'] != 1:
                            df.loc[a, 'labels'] = 1
        if len(ons) > 0 and len(zero) > 0:
            for i in range(max(zero)+1, min(ons)):
                df.loc[i, 'labels'] = 0
        i = min(ons)-1
        while min(ons)-i <= 4:
            if i >= df.index[0]:
                df.loc[i, 'labels'] = 1
                i = i - 1
            else:
                break
        return df

    def labelAndClassify(self, fileName):
        df = self.read_File(fileName)
        vectors = self.vectorizer.transform(df['Text'])
        pred = self.SVM_Model.predict_proba(vectors)
        pred = tuple(max(x) for x in pred)
        dff = self.SVM_Model.predict(vectors)
        df['labels'] = dff
        df['probability'] = pred
        return df

    def searchUnits(self, txt):
        sx = re.finditer(self.unitsRegx, txt)
        s = re.search(self.unitsRegx, txt)
        if s != None:
            return tuple({x.start(): x.group()} for x in sx)
        return None

    def findBullet(self, f, df, space):
        reg = ""
        if space:
            reg = self.spaceBulletRegex
        else:
            reg = self.bulletRegex
        indexes = {}
        for a, row in f.iterrows():
            if re.search(reg, row['Text']) != None:
                indexes[a] = [list((m.start()+1, m.start()+len(m.group(0).strip()), m.group(0).strip()))
                              if m.start() == 0 else [] for m in re.finditer(reg, row['Text'])][0]
        indexes = {k: v for k, v in indexes.items() if v != []}
        if not space:
            dotCount = 0
            for key, value in indexes.items():
                if value[2].count(".") >= 1:
                    dotCount += 1
            return dotCount
        else:
            spaceCount = 0
            for key, value in indexes.items():
                if value[2].count(" ") >= 1:
                    spaceCount += 1
            return spaceCount

    def findBulletTemplate(self, f, df):
        space = self.findBullet(f, df, True)
        dot = self.findBullet(f, df, False)
        if space > dot:
            return True
        return False

    def separateSections(self, df):
        f = df[df['labels'] == 1]
        space = True
        val = f.index.values
        oneIndex = -1
        for x in range(len(val)):
            if val[x+1]-val[x] <= 2:
                oneIndex = val[x]
                break
        if oneIndex != -1:
            f = df.iloc[oneIndex:]
        space = self.findBulletTemplate(f, df)
        sections, j = self.dotSections(f, df, space)
        return sections, j

    def makeIndexes(self, f, df, space):
        reg = ""
        if space:
            reg = self.spaceBulletRegex
        else:
            reg = self.bulletRegex
        indexes = {}
        for a, row in f.iterrows():
            if re.search(reg, row['Text']) != None:
                indexes[a] = [list((m.start(), m.start()+len(m.group(0).strip()), m.group(0).strip()))
                              if m.start() == 0 else [] for m in re.finditer(reg, row['Text'])][0]
        indexes = {k: v for k, v in indexes.items() if v != []}
        ids = []
        push = ids.append
        for key, value in indexes.items():
            v = df.iloc[key]['Text']
            try:
                if ' ,' in v[value[0]:value[1]+1] or ',' in v[value[0]:value[1]+1] or re.search(self.unitsOnly, v[value[0]:value[1]+1].lower()) != None or re.search(self.date, value[2]) != None:
                    push(key)
                if re.search(self.onlyUnits, v[value[1]:].split(' ')[1].lower()) != None or re.search(self.onlyUnits, v[value[1]+1:].split(' ')[0].lower()) != None:
                    sp = value[2].split(' ')
                    if len(sp) > 1:
                        indexes[key][2] = sp[0]
                    else:
                        if key not in ids:
                            push(key)
            except:
                pass
        for k in ids:
            del indexes[k]

        return indexes

    def dotSections(self, f, df, space):
        indexes = self.makeIndexes(f, df, space)
        indexKeys, bulletpoints = tree.driveCode(
            indexes, space, df)
        sections = []
        sections_push = sections.append
        j = 0
        allUnits = []
        allUnits_push = allUnits.append
        for id, key in enumerate(indexKeys):
            ind = key
            if id+1 <= len(indexKeys)-1:
                txt = df.iloc[key]['Text']
                ind += 1
                while ind < indexKeys[id+1]:
                    if 'von' not in df.iloc[ind]['Text'] and 'Übertrag:' not in df.iloc[ind]['Text'] and 'Seite' not in df.iloc[ind]['Text']:
                        txt += '\n' + df.iloc[ind]['Text']
                    ind += 1
                else:
                    # add 4 lines if second is greater
                    if ind > indexKeys[id+1]:
                        j = 0
                        while j < min(8, len(df)):
                            txt += '\n' + df.iloc[ind]['Text']
                            ind += 1
                            j += 1
            else:
                i = 0
                txt = df.iloc[ind]['Text']
                while True:
                    ind += 1
                    txt += '\n' + df.iloc[ind]['Text']
                    i += 1
                    if i >= 25 or ind == len(df)-1:
                        break
            try:
                heading = txt.split("\n")[0]
            except:
                heading = ""
            txt = txt.replace('\n', ' ')
            x = self.searchUnits(txt)
            allUnits_push(x)
            if len(sections) == 0:
                j = key
            sections_push(
                {"bullet": bulletpoints[id], 'extracted_line': txt, 'Heading': heading})
        self.unitSelection(sections, allUnits)
        if j == 0:
            j = len(df)
        return sections, j

    def separateUnit(self, unit):
        return re.sub('\s+', ' ', unit).split(" ")

    def refineText(self, txt, unit, bullet, heading, position):
        text = txt[len(heading):]
        text = text.replace(bullet, "")
        text = re.sub("(\\.)(\\.)+", "", text)
        text = re.sub('\s+', ' ', text)
        if unit != "":
            if position:
                text = text.replace(unit, "")
            else:
                id = text.find(unit)
                text = text[:id]
        return text

    def unitSelection(self, sections, units):
        start = 0
        end = 0
        for i in range(0, len(sections)):
            if units[i] != None:
                if len(units[i]) == 1:
                    l = len(sections[i]['extracted_line'])//3
                    if sections[i]['extracted_line'][:int(l)].find(str(list(units[i][0].values())[0])) == -1:
                        end += 1
                    else:
                        start += 1
        first = False
        if start > end:
            first = True
        for id in range(0, len(sections)):
            if units[id] == None:
                sections[id]['quantity'], sections[id]['Unit'] = "", ""
                sections[id]['extracted_text'] = self.refineText(
                    sections[id]['extracted_line'], "", sections[id]['bullet'], sections[id]['Heading'], True)
                sections[id]['Heading'] = sections[id]['Heading'].replace(
                    sections[id]['bullet'], '').strip()

            else:
                if first:
                    unit = list(units[id][0].values())[0]
                    qu = self.separateUnit(unit)
                    if len(qu) == 1:
                        unit_ex = re.split(self.unitsOnly, qu[0])
                        qu = [unit_ex[0], unit_ex[1]]
                    sections[id]['quantity'], sections[id]['Unit'] = qu[0], qu[1]
                    sections[id]['extracted_text'] = self.refineText(
                        sections[id]['extracted_line'], qu[0]+' '+qu[1], sections[id]['bullet'], sections[id]['Heading'], True)
                    sections[id]['Heading'] = sections[id]['Heading'].replace(
                        sections[id]['bullet'], '').strip()
                else:
                    unit = list(units[id][-1].values())[0]
                    qu = self.separateUnit(unit)
                    if len(qu) == 1:
                        unit_ex = re.split(self.unitsOnly, qu[0])
                        qu = [unit_ex[0], unit_ex[1]]
                    sections[id]['quantity'], sections[id]['Unit'] = qu[0], qu[1]
                    sections[id]['extracted_text'] = self.refineText(
                        sections[id]['extracted_line'], qu[0]+' '+qu[1], sections[id]['bullet'], sections[id]['Heading'], False)
                    sections[id]['Heading'] = sections[id]['Heading'].replace(
                        sections[id]['bullet'], '').strip()

        return sections

    def classify(self, fileName):
        df = self.labelAndClassify(fileName)
        green, k = self.separateSections(df)
        print("Seaparated")
        yellow = ''
        yellow = df[:k].copy(deep=True)
        yellow['Text'] = yellow['Text'].str.strip().replace(
            "\n", " ", regex=True).replace('  ', ' ')
        Data = {0: [{"Text": v['Text']} for k, v in yellow.iterrows()],
                1: green}
        return Data
