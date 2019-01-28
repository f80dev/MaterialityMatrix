#install docker
#sudo curl -sSL get.docker.com | sh

#pour les problemes de droit sur les répertoires : su -c "setenforce 0"

#arm
#FROM arm64v8/python
FROM armhf/python
#FROM resin/rpi-raspbian:stretch
#FROM hypriot/rpi-python

#docker build -t f80hub/material_matrix_arm . & docker push f80hub/material_matrix_arm:latest
#docker rm -f material_matrix && docker pull f80hub/material_matrix_arm:latest && docker run --restart=always -p 5000:5010 --name material_matrix -d f80hub/material_matrix_arm:latest



RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y

RUN apt-get remove python2.7 --purge -y

RUN apt-get install -y python3 python3-dev python3-pip

EXPOSE 5000

RUN mkdir /app
RUN mkdir /app/assets

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY assets /app/assets

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python", "app.py"]