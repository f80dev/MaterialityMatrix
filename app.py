from flask import Flask,jsonify,Response
from googlesearch import search,hits
import pandas as pd
from urllib.parse import urlparse

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


def urltodata(url:str):
    data: pd.DataFrame = None
    if ".xls" in url: data = pd.read_excel(url)
    if ".csv" in url: data = pd.read_csv(url, sep=";")
    return data


def extract_domain(url:str):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result

#test : http://localhost:5000/search/Michelin/temp.csv
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel

    audience=urltodata("https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv")
    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    for i in range(len(data)):
        row=data.iloc[i]
        result=search(brand+" & "+row["query"])
        classement=[]
        for r in result:
            domain=extract_domain(result)
            classement.push(audience[domain])

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
