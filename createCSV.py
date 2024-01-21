# create a folder named "test contracts" and put all pdfs in it
# create a folder named "test csvs" for csv saving


# import fitz
from pathlib import Path

# import fitz


from pprint import pprint
# from word2vec import get_all_embedding_w2v
# from collections import Counter
# from queue import Empty
import pdfminer
# from elasticsearch import Elasticsearch
# from elasticsearch import helpers
# from joblib import dump, load
# from sklearn.ensemble import RandomForestClassifier
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
import ray
# import re
# from pathlib import Path
# import requests,boto3


import io
import time
import datetime
import pandas as pd
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import numpy as np
import math
import re
import pdfplumber
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]


@ray.remote
def get_tables(a, page):
    tlist = list()
    # page = dl[a]
    try:
        for table in page.find_tables():
            if table:
                t = table.extract()
                if len(t) > 1:
                    colHeadings = t.pop(0)
                    jd = len(set.intersection(set(colHeadings), set(headText)))
                    if jd == len(set(colHeadings)) or jd == 0:
                        l, tp, rt, bt = table.bbox
                        tlist.append({'Page': a+1, "Columns": colHeadings, "Table": t, "BBox": {
                                     'Left': int(l), 'Top': int(tp), 'Right': int(rt), 'Bottom': int(bt)}})
    except Exception as ex:
        print(ex)
    if len(tlist) != 0:
        return tlist
    else:
        return None


def keep_visible_lines(obj):
    """
    If the object is a ``rect`` type, keep it only if the lines are visible.

    A visible line is the one having ``non_stroking_color`` as 0.
    """
    if obj['object_type'] == 'rect':
        # print("="*100)
        # print(obj['non_stroking_color'])
        # print(obj['non_stroking_color'][0] == 0)
        return obj['non_stroking_color'][0] == 0
    return True


def borderTableRower(cols, table):
    cis = list()
    for n, i in enumerate(cols):
        if i is None:
            cis.append(n)
    repo = cis
    jango = False
    tableRes = table
    jrows = list()
    jrows.append(cols)
    for p, row in enumerate(table):
        for n, col in enumerate(row):
            if len(cis) == 0:
                jango = True
                break
            if n in repo and col is not None:
                cis.pop(cis.index(n))
        if jango:
            break
        jrows.append(tableRes.pop(p))
    del cis
    prev = None
    nRows = list()
    for row in jrows:
        axe = list()
        for n in row:
            if n is None and prev is None:
                axe.append(" ")
                continue
            elif n is None and prev is not None:
                axe.append(prev)
            elif n is not None:
                prev = n
                continue
        nRows.append(axe)
    prev = None
    for row in jrows:
        if prev is None:
            prev = row
            continue
        else:
            for n, (x, y) in enumerate(zip(prev, row)):
                if x is None:
                    x = " "
                if y is None:
                    y = " "
                prev[n] = x+" "+y
    return prev, tableRes


def get_border_tables(file):
    global maxPageSize
    pdf = pdfplumber.open(file)
    page_1 = pdf.pages[0]

    maxPageSize = (page_1.height)
    print(time.time()-start)
    global dl
    ts = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
    }
    tbList = list()
    for a, page in enumerate(pdf.pages):
        page = page.filter(keep_visible_lines)
        colsList = list()
        for tables in page.find_tables(table_settings=ts):
            if type(tables) != list:
                tables = [tables]
            for table in tables:
                if table:
                    t = table.extract()  # _table(table_settings=ts)
                    # t=table
                    if len(t) > 1:
                        colHeadings = t.pop(0)
                        jd = len(set.intersection(
                            set(colHeadings), set(headText)))
                        if jd == len(set(colHeadings)) or jd == 0:
                            l, tp, rt, bt = table.bbox
                            colHeadings, t = borderTableRower(colHeadings, t)
                            tbList.append({'Page': a+1, "Columns": colHeadings, "Table": t, "BBox": {
                                'Left': int(l), 'Top': int(tp), 'Right': int(rt), 'Bottom': int(bt)}})

    print(time.time()-start)
    return tbList


def get_toc(fp):
    # # Open a PDF document.
    # fp = open(file, 'rb')
    parser = PDFParser(fp)

    document = PDFDocument(parser)
    toc = list()
    # Get the outlines of the document.
    try:
        outlines = document.get_outlines()
        for (level, title, dest, a, se) in outlines:
            if level <= 2:
                toks = title.split()
                # if re.match(r"[.\d]+",toks[0]):
                if len(toks) < 10:
                    # if not re.match(r"\([a-z]\)",toks[0]):
                    toc.append((level, title))
    except Exception as ex:
        print(ex)
    print(time.time()-start)
    if len(toc) == 0:
        toc = None
    return toc


def get_intersection(value, jinker):
    minx = value['Left']
    dy = value['Top']
    maxx = value['Left']+value['Width']
    retDict = dict()
    for ax, a in iter(jinker.items()):
        x, y, w, h = a
        x2 = x+w
        if y > dy:
            if minx < x and maxx > x and maxx <= x2:
                retDict[ax] = True
            elif maxx < x and minx >= x and minx <= x2:
                retDict[ax] = True
            elif minx >= x and minx <= x2 and maxx >= x and maxx <= x2:
                retDict[ax] = True
            elif minx < x and maxx > x2:
                retDict[ax] = True
            else:
                retDict[ax] = False
    count = 0
    for key, values in retDict.items():
        if values == True:
            count += 1
    if count == 1:
        return retDict
    else:
        return None


def get_REMatch(jaxx):
    if re.match(r'/\d\.\s+|\([a-z]\)\s+|\(.*?\)|[a-z]\)\s+|\[\d+\]$|\([0-9].*?\)|\w[.)]\s*|\([a-z]\)\s+|[a-z]\)\s+|•\s+|[A-Z]\.\s+|[IVX]+\.\s+/g', jaxx):
        return 2
    elif re.match(r'[0-9]*\n', jaxx):
        return 1
    elif re.match(r'^-?\d+(?:\.\d+)$', jaxx):
        return 1
    else:
        return 0


def zero(x):
    if len(x) == 2:
        if x["Is_Bullet"].tolist()[0] == 2:
            return pd.DataFrame({"Width": x["Width"].sum(), "Is_Bullet": x["Is_Bullet"].iloc[0],
                                 "Page": x["Page"].iloc[0], "Left": x["Left"].iloc[0], "Top": x["Top"].min(), "Height": x["Height"].max(),
                                 "Text": ' '.join(x['Text'].tolist()), "Font": ' '.join(list(set(x['Font'].tolist()))), "Size": ' '.join(list(set((x['Size'].tolist())))),
                                 "Font Count": len(' '.join(list(set(x['Font'].tolist()))).split(' '))}, index=[0])
        else:
            return x
    else:
        return x


def lp(page):
    try:
        interpreter.process_page(page)
        return device.get_result()
    except Exception as ex:
        print(ex)


def extract_page_layouts(pdf_file):
    """
    Extracts LTPage objects from a pdf file.
    modified from: http://www.degeneratestate.org/posts/2016/Jun/15/extracting-tabular-data-from-pdfs/
    Tests show that using PDFQuery to extract the document is ~ 5 times faster than pdfminer.
    """
    global toc
    laparams = LAParams()

    # with open('{}'.format(file), mode='rb') as pdf_file:
    print("Open document ")
    toc = get_toc(pdf_file)
    # if not document.is_extractable:
    #     raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    global device
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    global interpreter
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    layouts = []
    pages = PDFPage.get_pages(pdf_file, check_extractable=False)

    print(time.time()-start)
    layouts = [lp(page) for page in pages]
    print(time.time()-start)

    return layouts


def get_text_objects(page_layout):
    # do multi processing
    texts = []
    # seperate text and rectangle elements
    for elem in page_layout:
        if isinstance(elem, pdfminer.layout.LTTextBoxHorizontal) or isinstance(elem, pdfminer.layout.LTTextBox):
            texts.extend(elem)
        elif isinstance(elem, pdfminer.layout.LTTextLine) or isinstance(elem, pdfminer.layout.LTTextLineHorizontal):
            texts.append(elem)
    return texts


def get_data(element):
    pgno, element = element
    text = element.get_text()
    if not text.isspace():
        (x0, y0, x1, y1) = element.bbox
        w = x1-x0
        h = y1-y0
        deto = list(element)
        font = list()
        size = list()
        for deto in list(element):
            if isinstance(deto, pdfminer.layout.LTChar):
                font.append(deto.fontname)
                size.append(str(round(deto.size, 2)))
        font = list(set(font))
        size = list(set(size))
        return pd.DataFrame({"Width": int(float(w)), "Page": pgno, "Left": int(float(x0)), "Top": int(float(y1)), "Height": int(float(h)),
                             "Text": text, "Font": ' '.join(font), "Size": ' '.join(size), "Font Count": len(font)}, index=[0])


def get_text_data(objs, pgno):
    objs = [(pgno, obj) for obj in objs]
    p1 = ThreadPool(mp.cpu_count())
    dfs = p1.map(get_data, objs)
    p1.close()
    try:
        return pd.concat(dfs)
    except Exception as ex:
        print(ex)
        return None


def get_table_rects(lst):
    if lst is not None:
        jk = list()
        if len(lst) > 1:
            ele = lst.pop(0)
            for i in lst:
                if not is_intersect(i['BBox'], ele['BBox']):
                    jk.append(i)

            jk.extend(get_table_rects(lst))
            return jk
        else:
            jk.extend(lst)
            return jk


def is_intersect(r1, r2):
    if r1['Left'] >= r2['Left'] and r1['Right'] <= r2['Right'] and r1['Top'] <= r2['Top'] and r1['Bottom'] >= r2['Bottom']:
        return False
    # # if r1['Left'] > r2['Right'] or r1['Right'] < r2['Left']:
    # #     return False
    # # if r1['Top'] > r2['Bottom'] or r1['Bottom'] < r2['Top']:
    # #     return False
    return True
    # if r2['Left'] < r1['Left'] < r2['Right'] and r2['Top'] < r1['Top'] < r2['Bottom']:
    #     return False
    # else:
    #     return True


@ray.remote(num_cpus=0.2)
def hMerger(dpgno, adf):
    adt = [x.sort_values(
        "Left", inplace=False) for a, x in adf.groupby(["Top"])]
    p2 = ThreadPool(mp.cpu_count())
    adf = pd.concat(p2.map(zero, adt))
    p2.close()
    return adf


def getRowState(row):
    # print(row.values())
    states = dict()
    for key, text in row.items():
        if type(text) == str:
            if len(text) > 0:
                states[key] = "Text"

        elif not math.isnan(text):
            states[key] = "Text"
        elif math.isnan(text):
            states[key] = "No_Text"
    return states


def get_table_struct(tbdf):
    rows = list()
    for top, x in tbdf.groupby('Top'):
        row = dict()
        for jojo in x.to_dict('records'):
            row[jojo['column']] = jojo['Text']
        rows.append(row)

    return pd.DataFrame(rows)


@ray.remote(num_cpus=0.3)
def tb_detr(a, x, pgNo, ylvl):
    tbDF = pd.DataFrame()
    cols_cords = dict()
    cols_dict = dict()
    for jojo in x.to_dict('records'):
        cols_cords[jojo['Text']] = (
            jojo['Left'], jojo['Top'], jojo['Width'], jojo['Height'])

        cols_dict[jojo['Text']] = list()
        for b, y in ylvl:
            if b != a:
                for dodo in y.to_dict('records'):
                    rDic = get_intersection(dodo, cols_cords)
                    if rDic:
                        for key, value in rDic.items():
                            if value == True:
                                dodo['column'] = key
                                dodo['Right'] = dodo['Left']+dodo['Width']
                                dodo['Bottom'] = dodo['Top']+dodo['Height']
                                tbDF = tbDF.append(
                                    pd.DataFrame(dodo, index=[0]))
                                dodo['DP'] = (dodo['Left'], dodo['Top'])

                                cols_dict[key].append(dodo)
    if set(['Left', 'Bottom', 'Right', 'Top']).issubset(tbDF.columns):
        dek = {'Left': tbDF['Left'].min(), 'Top': tbDF['Bottom'].max(
        ), 'Right': tbDF['Right'].max(), 'Bottom': tbDF['Top'].min()}
    else:
        dek = None

    rowId = list()
    tble = dict()
    jd = len(set.intersection(set(cols_dict.keys()), set(headText)))
    if bool(cols_dict) and dek is not None and len(cols_dict.keys()) > 2 and (jd == len(set(cols_dict.keys())) or jd == 0):
        for key in cols_dict:
            try:
                if len(cols_dict[key]) != 0:
                    df = pd.DataFrame(cols_dict[key])
                    df = df.drop_duplicates(subset='DP')
                    rowId.extend(df['DP'].values.tolist())
                    tble[key] = df[["Text", "DP"]].to_dict('records')
                else:
                    tble = None
                    break
            except Exception as ex:
                iop = 0
    else:
        tble = None
    rowId = list(set(rowId))

    if bool(tble):
        return {"BBox": dek, "Page": pgNo, "Table": get_table_struct(tbDF), "Columns": list(tble.keys())}
    else:
        return None


def rowMerger(rows):
    print("="*200)
    newRows = list()
    changeState = False
    sChange = False
    states = "Empty"
    nrow = None
    for row in rows:
        if sChange:
            newRows.append(nrow)
            states = "Empty"
            nrow = None
            changeState = False
            sChange = False
            # continue
        if states == "Empty" and nrow is None:
            states = getRowState(row)
            nrow = row
            # continue
        elif states != "Empty":
            newState = getRowState(row)
            for key, state in newState.items():
                if states.get(key) != state:
                    if changeState == False:
                        changeState = True
                        states = newState
                        break
                    elif changeState:
                        sChange = True
                    break
            if sChange == False:
                for key in nrow.keys():
                    a = str(nrow.get(key))
                    b = str(row.get(key))
                    if a == "nan":
                        a = ""
                    if b == "nan":
                        b = ""

                    nrow[key] = a+b

    # print(newRows)
    if len(newRows) > 1:
        rows = newRows
    return rows


@ray.remote(num_cpus=0.3)
def blTD(pgNo, df):
    ylvl = df.groupby(["Top"])

    tablesList = ray.get([tb_detr.remote(a, x, pgNo, ylvl)
                          for a, x in ylvl if len(x) > 2])

    tablesList = [x for x in tablesList if x is not None]

    if len(tablesList) > 0:
        tl = get_table_rects(tablesList)
        print(tl[0].get('Table').keys())
        print('PageNo:{}'.format(pgNo))
        t2 = list()
        for t in tl:
            t["Table"] = t["Table"].to_dict("records")
        print(len(tl))
        return tl
    else:
        return None


def score(row):
    score = 0
    if 'Bold' in row['Font']:
        score += 1
    if maxFontStyle[0] not in row['Font']:
        score += 1
    if int(float(row['Size'])) > maxSize:
        score += int(float(row['Size'])) - maxSize
    if int(float(row['Size'])) < maxSize:
        score = 0
    if row['Font Count'] > 1:
        if len(row["Font"].split()) == len([x for x in row["Font"].split() if "Bold" in x]):
            score += 1
        elif row["Text"].isupper() and "Bold" in row["Font"]:
            score += 1
        else:
            score = 0
    # if row['TOC'] == 1:
    #     score = 0
    if row['Is_Bullet'] == 1:
        score = 0
    # if len(row["Text"].split()) > 7:
    #     score=0
    # if re.search(r'(\d+(?:\.\d+)*\.?(\d?))\s(\D*?)(\s?)(\d*)',row['Text']):
    #     score = 0
    return score


def toc_lines(row):
    if re.match(r'/\d\.\s+|\([a-z]\)\s+|\(.*?\)|[a-z]\)\s+|\[\d+\]$|\([0-9].*?\)|\w[.)]\s*|\([a-z]\)\s+|[a-z]\)\s+|•\s+|[A-Z]\.\s+|[IVX]+\.\s+/g', row['Text']):
        return 1
    else:
        return 0


def parse_layouts(layout, pg_no):
    try:
        return get_text_data(get_text_objects(layout), pgno=pg_no+1)
    except:
        return None


def colFix(m):
    if m is None:
        return "_"
    elif m.isspace():
        return "_"
    elif len(m) == 0 or m.strip() == "":
        return "_"
    elif m is None:
        return "_"
    elif len(m) != 0:
        return "{}".format(m).replace(".", "  ")


def extract_from_pdf(request=None):
    global toc
    global images
    interpreter = None
    device = None
    global max_page_width
    global maxPageSize
    global layouts, start, maxFontStyle, maxSize, headText
    if request is not None:
        pdf = open(request, 'rb')
        start = time.time()
        print(datetime.datetime.now())
        page_layouts = extract_page_layouts(pdf)

        print("Number of pages: %d" % len(page_layouts))
        final_df = pd.DataFrame()
        adf = list()
        adf = [parse_layouts(x, n) for n, x in enumerate(page_layouts)]
        adf = [x for x in adf if x is not None]
        final_df = pd.concat(adf)
        final_df['Size'] = final_df.Size.str.split(' ').apply(lambda x: max(
            [int(float(i)) for i in x if i is not None])).values.tolist()
        pdf.close()
        return final_df


def createCSVFile(pdf):
    df = extract_from_pdf("PdfFile/"+pdf)

    # df.to_csv("./{}/{}.csv".format("csvFile", pdf),
    #           index=False, encoding="utf-8-sig")
    return df
