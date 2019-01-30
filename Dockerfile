#install docker
#sudo curl -sSL get.docker.com | sh

#pour les problemes de droit sur les répertoires : su -c "setenforce 0"

#arm
#FROM arm64v8/python
#FROM armhf/python
#FROM resin/rpi-raspbian:stretch

FROM hypriot/rpi-python


#docker build -t f80hub/material_matrix_arm . & docker push f80hub/material_matrix_arm:latest
#docker rm -f material_matrix && docker pull f80hub/material_matrix_arm:latest && docker run --restart=always -p 5000:5010 --name material_matrix -d f80hub/material_matrix_arm:latest

RUN apt-get remove python2.7 --purge -y


RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y



RUN apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
RUN apt-get install libncursesw5-dev libgdbm-dev libc6-dev -y
RUN apt-get install zlib1g-dev libsqlite3-dev tk-dev -y
RUN apt-get install libssl-dev openssl -y
RUN apt-get install libffi-dev -y
RUN apt-get install -y python3
RUN apt-get autoremove -y
RUN wget https://github.com/python/cpython/archive/v3.7.1.tar.gz
RUN tar -xvf v3.7.1.tar.gz
WORKDIR v3.7.1
RUN ./configure --prefix=$HOME/.local --enable-optimizations && make && make altinstall


EXPOSE 5000

RUN mkdir /app
RUN mkdir /app/assets

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY assets /app/assets

RUN apt-get install -y python3-pip

RUN pip install --upgrade pip
RUN pip install setuptools
RUN pip install textblob
RUN pip install flask
RUN pip install google
RUN pip install pandas
RUN pip install xlrd
RUN pip install xlsxwriter
RUN pip install beautifulsoup4
RUN pip install requests

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python", "app.py"]