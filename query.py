import pandas as pd
from flask import send_file
import googlesearch
import os
from app import log
from document import Document
from tools import extract_domain, hash_str, get_words, urlToString, urlToHTML


class Query:
    name:str=""
    search:str=""
    brand:str=""
    documents:list=[]

    score = 1e10
    audience = 1e10
    polarite = 0
    subjectivite = 0


    def __init__(self,name:str,search:str,brand:str,exclude:str="",size:int=20,path:str=None):
        self.name=name
        self.search=search
        self.brand=brand
        self.exclude=exclude.lower().replace("$brand", brand.lower())

        self.google_query = "\"" + brand + "\" AND (" + search + ")"
        if not self.load_result(path):
            self.result = googlesearch.search(self.google_query, tbs="qdr:y", start=0, stop=size, user_agent="MyUserAgent2", pause=30)


    def load_result(self,path=""):
        if path is None:return False
        self.result=[]
        filename=path + "/" + hash_str(self.google_query)
        try:
            with open(filename, "r") as f:
                s=f.read()

            self.result=list(s.split("\n"))
            return True
        except:
            return False


    def save_result(self,path=""):
        filename=path+"/"+hash_str(self.google_query)
        try:
            os.remove(filename)
        except:
            pass
        f=open(filename,"xt")
        for r in self.result:
            log(r +" saved")
            f.write(r+"\n")
        f.close()


    def execute(self,domain_to_exclude:str="",densite:int=250):
        log("traitement de " + self.search)
        for r in self.result:  # Ouverture de la page
            if len(r)>0:
                log("traitment de " + r)
                domain = extract_domain(r)

                exclude_domain: str = self.exclude.split(" ") + domain_to_exclude

                if not domain in exclude_domain:
                    d = Document(r)
                    d.analyse(densite=densite)
                    self.documents.append(d)
                else:
                    log("=> rejected because of forbidden domain")


    def init_metrics(self,size):
        for d in self.documents:
            self.audience += d.audience
            self.polarite += d.polarite
            self.subjectivite += d.subjectivite

        n_rows = float(len(self.documents))
        if n_rows>0:
            self.audience=self.audience/n_rows
            self.polarite=self.polarite/n_rows
            self.subjectivite=self.subjectivite/n_rows


    def to_dict(self):
        rc=dict({
            "name":self.name,
            "query":self.google_query,
            "score":self.score,
            "audience":self.audience,
            "polarite":self.polarite,
            "subjectivite":self.subjectivite,
            "documents":[]
        })
        for d in self.documents:
            rc["documents"].append(d.to_dict())
        return rc


    def to_df(self):
        lst_cols = ["index", "audience", "score"]
        size = 30
        for i in range(size):
            lst_cols = lst_cols + ["url" + str(i)]
        rc = pd.DataFrame(columns=lst_cols)

        # classements: pd.DataFrame = pd.DataFrame(columns=["audience", "ranking", "polarite", "subjectivite", "url"])
        # for d in self.documents:
        #     classements.append(d.to_df())
        return rc


    def to_excel(self):
        writer = pd.ExcelWriter("./saved/output.xlsx", engine="xlsxwriter")
        self.to_df().to_excel(excel_writer=writer, sheet_name="output")
        writer.save()
        return send_file("./saved/output.xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         attachment_filename=self.brand + ".xlsx", as_attachment=True)


    def to_csv(self):
        os.remove("./saved/output.csv")
        # q.to_csv("./saved/output.csv", sep=";", line_terminator="\n", index=False, decimal=".")
        return send_file("./saved/output.csv",
                         mimetype="text/csv",
                         attachment_filename=self.brand + ".csv", as_attachment=True)

    def project(self,words):
        i=0
        rc=[]
        for d in self.documents:
            r=d.project(words)
            if not r is None:
                rc.append([self.name,d.title,d.url]+r)

        return rc

