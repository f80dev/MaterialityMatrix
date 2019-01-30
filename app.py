from flask import Flask,jsonify,Response,request,send_file
from bs4 import BeautifulSoup
from googlesearch import search
import pandas as pd
import os
from urllib.parse import urlparse
from urllib.request import urlopen,Request
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome on MaterialityMatrix'


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


def urlToHTML(url:str):
    req=Request(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
    try:
        page = urlopen(req)
        return BeautifulSoup(page, "lxml")
    except:
        return None


def urlToString(soup:BeautifulSoup):
    if soup==None:return ""
    try:
        for script in soup(["script", "style"]):
            script.extract()

        return soup.getText()
    except:
        return ""


def maxCaracteres(text:str):
    paragraphes=text.split("\n")
    max=0
    for p in paragraphes:
        if len(p)>max:max=len(p)
    return max



def hash(df:pd.DataFrame):
    rc=df.memory_usage(deep=True)
    return str(sum(list(rc)))



#test : http://localhost:5000/search/Microsoft/rse.xlsx?format=xls
#test2:http://localhost:5000/search/Servier/rse.xlsx?format=xls
#test2:http://localhost:5000/search/Michelin/rse.xlsx?format=xls
#test2:http://192.168.1.72:5000/search/Servier/rse.xlsx?format=xls
#test2:http://ss.shifumix.com:5000/search/Altice/finances.xlsx?format=xls
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    print("Lancement du traitement pour "+brand)
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel

    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    audiences = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv",
                         index=1, sep=",")

    dt = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/domain_to_exclude.csv",sep=",")
    domain_to_exclude=list(dt.index.values)

    #fabrication du dataframe de reponse
    lst_cols=["index","audience","score"]
    size = 30
    for i in range(size):
        lst_cols=lst_cols+["url"+str(i)]
    rc=pd.DataFrame(columns=lst_cols)


    filename=hash(data)+"_"+brand+".pickle"
    if filename in os.listdir("./saved"):
        rc=pd.read_pickle("./saved/"+filename)
    else:
        for i in range(len(data)):
            idx = data.index.values[i]
            print("traitement de "+idx)
            row=data.iloc[i] #Contient chaque ligne du fichier d'input

            google_query="\""+brand+"\" AND ("+row["query"]+")"

            result=search(google_query,start=0,stop=size,user_agent="MyUserAgent2",pause=30)

            classements:pd.DataFrame=pd.DataFrame(columns=["audience","ranking","polarite","subjectivite","url"])
            j=0
            rank=0
            for r in result: #Ouverture de la page
                print("traitment de "+r)
                rank=rank+1
                domain=extract_domain(r)
                to_exclude:str=str(row["exclude"].lower()).replace("$brand",brand.lower())
                exclude_domain:str=to_exclude.split(" ")+domain_to_exclude
                if not domain in exclude_domain:
                    page=urlToHTML(r)
                    text = urlToString(page)
                    if len(text) > 0:
                        mc = maxCaracteres(text)
                        if mc>row["densite"]:
                            sentiment = [0, 0] #Initialisation du caractère positif/negatif et subjectif de la page
                            blob = TextBlob(text)
                            sentiment=blob.sentiment
                        else:
                            print("=> rejected because of density filter")

                        try:
                            classement=1e6-audiences.loc[domain][0]
                        except:
                            classement=1e6

                        classements.loc[j]=[classement,rank,sentiment[0],sentiment[1],r]
                        j=j+1
                else:
                    print("=> rejected because of forbidden domain")


            n_rows=float(len(classements))
            print(str(n_rows)+" rows to treat")
            if n_rows>0:
                score=20*(sum(classements["audience"]/1e6)/n_rows)
                audience=sum(classements["audience"]) / n_rows
                urls=list(classements["url"])
                polarite=sum(classements["polarite"])/n_rows
                subjectivite=sum(classements["subjectivite"])/n_rows
            else:
                score=1e10
                audience=1e10
                urls=[""]*size
                polarite=0
                subjectivite=0

            while len(urls)<size:
                urls=urls+[""]

            d_cols=dict({"index":idx,"score":score,"audience":audience,"polarite":polarite,"subjectivite":subjectivite})
            for i in range(size):
                d_cols["url"+str(i)]=urls[i]

            rc=rc.append(d_cols,ignore_index=True)

        rc.to_pickle("./saved/"+filename)

    if "format" in request.args:
        if str(request.args["format"]).startswith("xls"):
            try:
                os.remove("./saved/output.xlsx")
            except:
                pass
            writer = pd.ExcelWriter("./saved/output.xlsx",engine="xlsxwriter")
            rc.to_excel(excel_writer=writer,sheet_name="output")
            writer.save()
            return send_file("./saved/output.xlsx",
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             attachment_filename=brand+".xlsx", as_attachment=True)

        if request.args["format"]=="csv":
            os.remove("./saved/output.csv")
            rc.to_csv("./saved/output.csv",sep=";",line_terminator="\n",index=False,decimal=".")
            return send_file("./saved/output.csv",
                             mimetype="text/csv",
                             attachment_filename=brand+".csv", as_attachment=True)

    return jsonify(rc)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=False)
