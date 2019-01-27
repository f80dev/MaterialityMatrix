from flask import Flask,jsonify,Response,request,send_file
from googlesearch import search
import pandas as pd
import io
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

def insert_row(idx, df, df_insert):
    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop = True)

#test : http://localhost:5000/search/Arkema/rse.xlsx?format=xls
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel


    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    audience = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv",
                         index=1, sep=",")
    rc=pd.DataFrame(columns=["index","audience","score","urls"])
    for i in range(len(data)):
        row=data.iloc[i]
        google_query=brand+" AND ("+row["query"]+")"
        result=search(google_query,start=0,stop=20)
        classements:pd.DataFrame=pd.DataFrame(columns=["audience","ranking","url"])
        j=0
        rank=0
        for r in result:
            rank=rank+1
            domain=extract_domain(r)
            if not domain in row["exclude"]:
                try:
                    classement=audience.loc[domain][0]
                except:
                    classement=1e6

                classements.loc[j]=[classement,rank,r]
                j=j+1


        idx=data.index.values[i]
        n_rows=float(len(classements))
        if n_rows>0:
            score=sum((classements["audience"]/1e5)*classements["ranking"])/n_rows
            audience=sum(classements["audience"]) / n_rows
        else:
            score=1e10
            audience=1e10

        rc=rc.append({"index":idx,"score":score,"audience":audience,"urls":",".join(classements["url"])},ignore_index=True)





    if "format" in request.args:
        if request.args["format"]=="xls":
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            rc.to_excel(excel_writer=writer,sheet_name="output")
            return send_file(output,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             attachment_filename=".\output.xlsx", as_attachment=True)

    return jsonify(rc)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
