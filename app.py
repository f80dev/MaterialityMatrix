from flask import Flask,jsonify,Response,request,send_file
from googlesearch import search
import pandas as pd
import os
from urllib.parse import urlparse
from urllib.request import urlopen
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
    print(result)
    if len(result.split("."))>2:
        return result.split(".")[1]+"."+result.split(".")[2]
    else:
        return result


def urlToString(url:str):
    page = urlopen(url)
    text = page.read().decode("utf8")
    return text


def hash(df:pd.DataFrame):
    rc=df.memory_usage(deep=True)
    return str(sum(list(rc)))



#test : http://localhost:5000/search/Arkema/rse.xlsx?format=xls
@app.route('/search/<string:brand>/<string:referentiel>', methods=['GET'])
def searchforbrand(brand:str,referentiel:str):
    if not referentiel.startswith("http"):
        referentiel="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/"+referentiel



    data=urltodata(referentiel)
    if data is None:return Response("Bad format",401)

    audiences = urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/audience.csv",
                         index=1, sep=",")

    domain_to_exclude=list(
                            urltodata(url="https://raw.githubusercontent.com/f80dev/MaterialityMatrix/master/assets/domain_to_exclude.csv",sep=",").values
                           )

    #fabrication du dataframe de reponse
    lst_cols=["index","audience","score"]
    size = 20
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
            row=data.iloc[i]

            google_query=brand+" AND ("+row["query"]+")"

            result=search(google_query,start=0,stop=size,user_agent="MyUserAgent2",pause=30)

            classements:pd.DataFrame=pd.DataFrame(columns=["audience","ranking","url"])
            j=0
            rank=0
            for r in result: #Ouverture de la page
                rank=rank+1
                domain=extract_domain(r)
                exclude_domain:str=row["exclude"].lower().split(" ")+domain_to_exclude
                if not domain in exclude_domain:
                    text=urlToString(r)
                    if len(text)>0:
                        blob = TextBlob(text)
                        sentiment=blob.sentiment
                    else:
                        sentiment={}

                    try:
                        classement=1e6-audiences.loc[domain][0]
                    except:
                        classement=1e6

                    classements.loc[j]=[classement,rank,sentiment,r]
                    j=j+1
                else:
                    print(domain+" rejected")


            n_rows=float(len(classements))
            print(str(n_rows)+" rows to treat")
            if n_rows>0:
                score=20*(sum(classements["audience"]/1e6)/n_rows)
                audience=sum(classements["audience"]) / n_rows
                urls=list(classements["url"])
            else:
                score=1e10
                audience=1e10
                urls=[""]*size

            while len(urls)<size:
                urls=urls+[""]

            d_cols=dict({"index":idx,"score":score,"audience":audience})
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
                             attachment_filename="output.xlsx", as_attachment=True)

        if request.args["format"]=="csv":
            os.remove("./saved/output.csv")
            rc.to_csv("./saved/output.csv",sep=";",line_terminator="\n",index=False,decimal=".")
            return send_file("./saved/output.csv",
                             mimetype="text/csv",
                             attachment_filename="output.csv", as_attachment=True)

    return jsonify(rc)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=False)
