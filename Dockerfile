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


RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y

RUN apt-get remove python2.7 --purge -y


RUN apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
RUN apt-get install -y libssl-dev openssl libffi-dev

RUN wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tar.xz
RUN tar xf Python-3.7.2.tar.xz
WORKDIR Python-3.7.2
RUN ./configure
RUN make
RUN make altinstall


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