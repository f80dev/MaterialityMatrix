import re
import hashlib
import math
import os
import pickle

from nltk.corpus import stopwords
from io import StringIO
from urllib.parse import urlparse
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import pandas as pd
from textblob import TextBlob


def urltodata(url:str,index=0,sep=";"):
    data: pd.DataFrame = None
    if ".xls" in url: data = pd.read_excel(url,index_col=index)
    if ".csv" in url: data = pd.read_csv(url, sep=sep,index_col=index)
    return data


def extract_domain(url:str):
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    if len(result.split("."))>2:
        return result.split(".")[1]+"."+result.split(".")[2]
    else:
        return result

def extract_emails(text:str):
    if text is None:return list()
    match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    return match

def maxCaracteres(text:str):
    paragraphes=text.split("\n")
    max=0
    for p in paragraphes:
        if len(p)>max:max=len(p)
    return max


def hash_str(s:str):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def remove_file(path):
    try:
        os.remove(path)
        return True
    except:
        return False


def hash(df:pd.DataFrame):
    rc=df.memory_usage(deep=True)
    return str(sum(list(rc)))


def log(s:str):
    print(s)

#Trouver les mots importants dans un text par rapport à une collection de corpus
def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def stop_words():
    wrd_to_remove = stopwords.words(["french", "english"])
    for w in ["les", "d'une", "cette", "comme", "aussi", "plus", "moins"]: wrd_to_remove.append(w)
    return wrd_to_remove

def get_words(text:str,n_words:int=20):
    mc = maxCaracteres(text)
    if mc > 200:
        blob = TextBlob(text)
        wrds=blob.word_counts
        wrds_sorted= sorted(wrds.items(), key=lambda kv: kv[1],reverse=True)

        n_wrds_sorted= [w for w in wrds_sorted if not w[0] in stop_words() and len(w[0])>2]
        rc=[]
        for w in n_wrds_sorted[0:min(n_words,len(n_wrds_sorted))]:
            rc.append(w[0])
        return rc
    else:
        return None



def urlToHTML(url:str,req=None):
    if url is None or len(url)==0:return None

    try:
        req=Request(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
        page = urlopen(req)
        if "pdf" in page.headers["Content-Type"]:
            return convert_pdf_to_txt(url)
        else:
            return BeautifulSoup(page, "lxml")
    except:
        return None


def cache(body=None,name=None):
    filename = "./temp/" + name
    if body is None:
        try:
            with open(filename+".pkl", "rb") as f:
                return pickle.load(f)
        except:
            return None
    else:
        remove_file(filename)
        with open(filename, "w") as f:
            pickle.dump(body,f,protocol=pickle.DEFAULT_PROTOCOL)


def urlToString(soup:BeautifulSoup):
    if soup==None:return ""
    try:
        for script in soup(["script", "style"]):
            script.extract()

        return soup.getText()
    except:
        return ""


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    data = urlopen(path).read()
    f = open('output.pdf', 'wb')
    f.write(data)
    f.close()
    f = open("output.pdf","rb")

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(f, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    f.close()

    device.close()
    retstr.close()
    return text