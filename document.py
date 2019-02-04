import pandas as pd
from textblob import TextBlob, WordList

from tools import urlToHTML, urlToString, maxCaracteres, log, get_words


class Document:
    url:str=""
    score:int = 1e10
    audience:int= 1e10
    polarite:int = 0
    subjectivite:int= 0
    words=[]
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

    def analyse(self,densite):
        if type(self.page) == str:
            text = self.page
        else:
            text = urlToString(self.page)

        if len(text) > 0:
            mc = maxCaracteres(text)
            if mc > densite:
                self.blob = TextBlob(text)
                sentiment=self.blob.sentiment
                self.polarite = sentiment[1]
                self.subjectivite=sentiment[0]
                self.words = get_words(text,200)
                self.lang=self.blob.detect_language()
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
            "polarite": self.polarite,
            "subjectivite": self.subjectivite
        })
        return rc

    def to_df(self):
        rc: pd.DataFrame = pd.DataFrame(columns=["audience", "score", "polarite", "subjectivite", "words"])
        rc.append([self.audience,self.score,self.polarite, self.subjectivite, self.words])
        return rc