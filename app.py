import urllib

from flask import Flask,jsonify,Response,request,redirect
import pandas as pd
import os
from urllib.parse import urlparse, urlencode, quote_plus
from urllib.request import urlopen,Request
from textblob import TextBlob, WordList

from tools import log, urltodata, get_words, urlToString, urlToHTML
from query import Query

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome on MaterialityMatrix'


#test : http://localhost:5000/search/Microsoft/rse.xlsx?format=xls
#test2:http://localhost:5000/search/Servier/rse.xlsx?format=xls
#test2:http://localhost:5000/search/Michelin/rse.xlsx?format=xls
#http://localhost:5000/search/Renault/ef.xlsx?format=json
#test2:http://192.168.1.72:5000/search/Servier/rse.xlsx?format=xls
#test2:http://ss.shifumix.com:5000/search/Altice/finances.xlsx?format=xls
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    log("Lancement du traitement pour " + brand)

    format="json"
    if "format" in request.args:format=request.args["format"]

    size=3
    if "size" in request.args: size= int(request.args["size"])

    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel

    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    audiences = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv",
                         index=1, sep=",")

    dt = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/domain_to_exclude.csv",sep=",")
    domain_to_exclude=list(dt.index.values)

    if "xls" in format:
        filename=hash(data)+"_"+brand+".pickle"
        if filename in os.listdir("./saved"):
            return pd.read_pickle("./saved/"+filename)


    #words=get_words(urlToString(urlToHTML("https://fr.wikipedia.org/wiki/Responsabilit%C3%A9_soci%C3%A9tale_des_entreprises")), 30)
    words = get_words(urlToString(urlToHTML("https://fr.wikipedia.org/wiki/%C3%89vasion_fiscale")), 40)
    dt=pd.DataFrame(columns=["name","url"]+words)
    for i in range(len(data)):
        row=data.iloc[i] #Contient chaque ligne du fichier d'input

        q=Query(
            name=data.index.values[i],
            search=row["query"],
            brand=brand,
            exclude=row["exclude"],
            size=size,path="./temp")

        q.save_result("./temp")
        q.execute(domain_to_exclude=domain_to_exclude,densite=row["densite"])
        q.init_metrics(size)
        rows=pd.DataFrame(q.project(words = words),columns=["query","name","url"]+words)
        dt=dt.append(rows)

    if "xls" in format:return q.to_excel()
    if "csv" in format:return q.to_csv()
    if "redirect" in format:
        url=urllib.parse.quote_plus(request.url.replace("format=redirect","format=json"))
        return redirect(url+"https://jsoneditoronline.org/?url="+url)

    return jsonify(q.to_dict())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=False)
