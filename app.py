from flask import Flask,jsonify
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
    pd.read_excel()
    result=hits(brand+" & ('innovation incrementale' | 'innovation participative')")
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
