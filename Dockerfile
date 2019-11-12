#install docker
#sudo curl -sSL get.docker.com | sh

#docker build -t f80hub/materiality_matrix_x86 . & docker push f80hub/materiality_matrix_x86:latest
#pour les problemes de droit sur les répertoires : su -c "setenforce 0"
#docker rm -f materiality_matrix_x86 && docker pull f80hub/materiality_matrix_x86:latest && docker run --restart=always -v /root/certs:/app/certs -p 6000:6000 --name materiality_matrix_x86 -d f80hub/materiality_matrix_x86:latest 6000 ssl


#x86
FROM python:3.7.4-alpine


#arm
#FROM arm64v8/python
#FROM armhf/python
#FROM resin/rpi-raspbian:stretch

# Install dependencies
#RUN sudo apt-get update -y
#RUN sudo apt-get dist-upgrade
#RUN sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv --no-install-recommends && ln -s /usr/bin/python3 /usr/bin/python && rm -rf /var/lib/apt/lists/*


#FROM hypriot/rpi-python
#RUN apt-get update -y
#RUN apt-get upgrade -y
#RUN apt-get dist-upgrade -y
#RUN apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
#RUN apt-get install libncursesw5-dev libgdbm-dev libc6-dev -y
#RUN apt-get install zlib1g-dev libsqlite3-dev tk-dev -y
#RUN apt-get install libssl-dev openssl -y
#RUN apt-get install libffi-dev -y
#RUN apt-get install -y python3
#RUN apt-get autoremove -y
#RUN wget https://github.com/python/cpython/archive/v3.7.1.tar.gz
#RUN tar -xvf v3.7.1.tar.gz
#WORKDIR v3.7.1
#RUN ./configure --prefix=$HOME/.local --enable-optimizations && make && make altinstall

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
RUN pip3 -v install Flask
RUN apk add py3-numpy
RUN apk add py3-scipy

RUN apk --no-cache --update-cache add gcc g++ gfortran python python3-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN apk add cython
RUN pip3 -v install pandas

RUN pip3 install document
RUN pip3 install textblob
RUN pip3 install idna
RUN pip3 install PyPDF2
RUN pip3 install xlrd
RUN pip3 install xlsxwriter
RUN pip3 install beautifulsoup4
RUN pip3 install pdfminer.six
RUN pip3 -v install flask-cors

RUN apk add py-setuptools
RUN apk add  --no-cache --update-cache libxml2-dev libxslt-dev
RUN easy_install -v google-search

RUN apk add py3-openssl


EXPOSE 6000
VOLUME /certs

RUN mkdir /app
WORKDIR /app
COPY . /app

ENTRYPOINT ["python", "app.py"]