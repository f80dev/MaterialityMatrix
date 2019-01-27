from flask import Flask,jsonify,Response
from googlesearch import search,hits
import pandas as pd
from urllib.parse import urlparse

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


def urltodata(url:str,index=0,sep=";"):
    data: pd.DataFrame = None
    if ".xls" in url: data = pd.read_excel(url,index_col=index)
    if ".csv" in url: data = pd.read_csv(url, sep=sep,index_col=index)
    return data


def extract_domain(url:str):
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    print(result)
    if len(result.split("."))>2:
        return result.split(".")[1]+"."+result.split(".")[2]
    else:
        return result

#test : http://localhost:5000/search/Michelin/rse.xlsx
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel


    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    audience = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv",
                         index=1, sep=",")
    rc=[]
    for i in range(len(data)):
        row=data.iloc[i]
        result=search(brand+" & "+row["query"],start=0,stop=20)
        classements:pd.DataFrame=pd.DataFrame(columns=["audience","ranking"])
        j=1
        for r in result:
            domain=extract_domain(r)
            try:
                classement=audience.loc[domain][0]
            except:
                classement=1e6

            classements.loc[j]=[classement,j]
            j=j+1

        n_rows=float(len(classements))
        if n_rows>0:
            classement_moy={'index':data[0],'audience':sum(classements["audience"]) / n_rows,"score":sum((classements["audience"]/1e5)*classements["ranking"])/n_rows}
        else:
            classement_moy={'index':data[0],'audience':1e10,"score":1e10}

        rc.append(classement_moy)

    return jsonify(rc)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
