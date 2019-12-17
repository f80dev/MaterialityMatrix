import pandas as pd
from idna import unicode
from textblob import TextBlob

from tools import urlToHTML, urlToString, maxCaracteres, log, get_words, hash_str, remove_file, extract_emails

class Document:
    url:str=""
    score:int = 1e10
    audience:int= 1e10
    polarite:int = 0
    subjectivite:int= 0
    words=[]
    emails=list()
    page=None
    lang=""
    blob=None
    title=""

    def __init__(self, url:str):
        self.url=url
        if len(url)>0:
            self.page = urlToHTML(self.url)
            try:
                self.title=self.page.title.string
            except:
                pass

    def extract_email(self):
        try:
            self.emails=extract_emails(self.page)
            log("Mail récupérés = "+str(self.emails))
        except:
            log("Pas de récupération des mail")

    def analyse(self,densite):
        if type(self.page) == str:
            text = self.page
        else:
            text = urlToString(self.page)


        if len(text) > 0:
            mc = maxCaracteres(text)
            if mc > densite:
                try:
                    self.blob = TextBlob(text)
                    print("Analyse du sentiment -> ",end="")
                    sentiment=self.blob.sentiment
                    self.polarite = sentiment[1]
                    self.subjectivite=sentiment[0]
                    print("Mots clés -> ", end="")
                    self.words = get_words(text,200)
                    print("langue -> ", end="")
                    self.lang=self.blob.detect_language()
                except:
                    print("Erreur de traitement sur les analyses")
            else:
                log("=> rejected because of density filter")

    def project(self,words):
        if not self.blob is None:
            tab = self.blob.word_counts
            result= [w for w in tab.keys() if w in words]
            rc=[]
            for w in words:
                rc.append(tab[w])
            return rc
        else:
            return None


    def to_dict(self):
        if self.page is None:return None
        rc=dict({
            "url": self.url,
            "title":self.title,
            "score": self.score,
            "lang":self.lang,
            "audience": self.audience,
            "emails":self.emails,
            "polarite": self.polarite,
            "subjectivite": self.subjectivite
        })
        return rc

    def to_df(self):
        rc: pd.DataFrame = pd.DataFrame(columns=["audience", "score", "polarite", "subjectivite", "words"])
        rc.append([self.audience,self.score,self.polarite, self.subjectivite, self.words])
        return rc

    def saveDocument(self):
        filename="./temp/"+hash_str(self.url)+".html"
        remove_file(filename)
        with open(filename,"w") as f:
            f.write(unicode(self.page))
        f.close()

    def loadDocument(self):
        filename = "./temp/" + hash_str(self.url) + ".html"
        try:
            with open(filename, "rb") as f:
                self.page=f.read()
            f.close()
            return True
        except:
            return False
