#install docker
#sudo curl -sSL get.docker.com | sh

#Construction et installation de l'image
#docker build -t f80hub/materiality_matrix_arm . & docker push f80hub/materiality_matrix_arm:latest
#docker build -t f80hub/materiality_matrix_x86 . & docker push f80hub/materiality_matrix_x86:latest
#pour les problemes de droit sur les répertoires : su -c "setenforce 0"
#docker rm -f materiality_matrix_arm && docker pull f80hub/materiality_matrix_arm:latest && docker run --restart=always -p 7080:7080 --name materiality_matrix_arm -d f80hub/materiality_matrix_arm:latest 7080


#arm
#FROM f80hub/scientist_python_server_arm

#x86
FROM python:3.7.4-alpine


#arm
#FROM arm64v8/python
#FROM armhf/python
#docker build -t f80hub/materiality_matrix_arm . & docker push f80hub/materiality_matrix_arm:latest

#FROM resin/rpi-raspbian:stretch

# Install dependencies
#RUN sudo apt-get update -y
#RUN sudo apt-get dist-upgrade
#RUN sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv --no-install-recommends && ln -s /usr/bin/python3 /usr/bin/python && rm -rf /var/lib/apt/lists/*


#docker build -t f80hub/cluster_bench_arm . & docker push f80hub/cluster_bench_arm:latest
#docker rm -f clusterbench && docker pull f80hub/cluster_bench_arm:latest
#docker run --restart=always -p 5000:5000 --name clusterbench -d f80hub/cluster_bench_arm:latest

#test:docker run -p 5000:5000 -t f80hub/cluster_bench_x86:latest


#test SocketServer : http://45.77.160.220:5000

#arm
#docker build -t hhoareau/cluster_bench_arm .
#docker push hhoareau/cluster_bench_arm:latest

RUN apk update
RUN apk --update add python

RUN pip3 install --upgrade pip

#Installation des librairies complémentaires
RUN pip3 install document

RUN pip3 install idna
RUN pip3 install PyPDF2
RUN pip3 install xlrd
RUN pip3 install xlsxwriter
RUN pip3 install beautifulsoup4

RUN apk --no-cache --update-cache add gcc g++ gfortran python python3-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN pip3 install cython

RUN apk add py-setuptools
RUN apk add  --no-cache --update-cache libxml2-dev libxslt-dev
RUN easy_install -v google-search

RUN pip3 install textblob
RUN python3 -m textblob.download_corpora

RUN apk add py3-openssl
RUN pip3 install nltk
RUN pip3 install pdfminer.six

EXPOSE 6000
VOLUME /certs

RUN mkdir -p /app
WORKDIR /app
COPY . /app

ENTRYPOINT ["python", "app.py"]