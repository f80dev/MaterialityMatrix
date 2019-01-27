from flask import Flask,jsonify,Response
from googlesearch import search,hits
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


#test : http://localhost:5000/search/Michelin
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel

    data:pd.DataFrame=None
    if ".xls" in referentiel:data=pd.read_excel(referentiel)
    if ".csv" in referentiel:data=pd.read_csv(referentiel)
    if data is None:return Response("Bad format",401)

    for r in data.iterrows():
        result=hits(brand+" & "+r["google"])

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
