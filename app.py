import ssl
import sys
from flask import Flask, Response, request, json
import pandas as pd
import os
from flask_cors import CORS
from tools import log, urltodata, get_words, urlToString, urlToHTML

app = Flask(__name__)

@app.route('/')
def help():
    return 'Welcome on MaterialityMatrix'

#http://localhost:6000/search/GNIS/rse.xlsx
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
        filename=str(hash(str(data)))+"_"+brand+".pickle"
        if filename in os.listdir("./saved"):
            return pd.read_pickle("./saved/"+filename)


    words=get_words(urlToString(urlToHTML("https://fr.wikipedia.org/wiki/Responsabilit%C3%A9_soci%C3%A9tale_des_entreprises")), 30)
    #words = get_words(urlToString(urlToHTML("https://fr.wikipedia.org/wiki/%C3%89vasion_fiscale")), 40)
    dt=pd.DataFrame(columns=["name","url"]+words)

    result = dict()
    result["analyses"]=list()

    for i in range(len(data)):
        row=data.iloc[i] #Contient chaque ligne du fichier d'input

        if row["Execute"]:
            from query import Query
            q=Query(
                name=data.index.values[i],
                search=row["query"],
                brand=brand,
                exclude=row["exclude"],
                size=size,path="./temp")

            q.save_result("./temp")
            try:
                q.execute(domain_to_exclude=domain_to_exclude,densite=row["densite"])
                q.init_metrics(size)
                result["analyses"].append(q.to_dict())
                rows = pd.DataFrame(q.project(words=words), columns=["query", "name", "url"] + words)
                dt = dt.append(rows)
            except:
                print("Erreur de traitement pour "+q.name)
                pass

    #if "xls" in format: return q.to_excel()
    # if "csv" in format:return q.to_csv()
    # if "redirect" in format:
    #     url=urllib.parse.quote_plus(request.url.replace("format=redirect","format=json"))
    #     return redirect("https://jsoneditoronline.org/?url="+url)


    result["projection"]=dt.to_dict()

    # writer = pd.ExcelWriter("./saved/analyse.xlsx", engine="xlsxwriter")
    # result["analyses"].to_df().to_excel(excel_writer=writer, sheet_name="output")
    # writer.save()

    return app.response_class(response=json.dumps(result),status=200,mimetype="application/json")

if __name__ == '__main__':
    CORS(app)
    _port = sys.argv[1]
    if "debug" in sys.argv:
        app.run(host="0.0.0.0", port=_port, debug=True)
    else:
        if "ssl" in sys.argv:
            # Le context de sécurisation est chargé avec les certificats produit par "Let's Encrypt"
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain("/app/certs/fullchain.pem", "/app/certs/privkey.pem")
            app.run(host="0.0.0.0", port=_port, debug=False, ssl_context=context)

        else:
            # Le serveur peut être déployé en mode non sécurisé
            # cela dit la plus part des front-end ne peuvent être hébergés quand mode https
            # ils ne peuvent donc appeler que des serveurs en https. Il est donc préférable
            # de déployer l'API sur un serveur sécurisé
            app.run(host="0.0.0.0", port=_port, debug=False)

