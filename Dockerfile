from ubuntu:20.04

workdir /code

run apt update && apt install -y python3.9 && apt install -y python3-pip

run apt install -y git

run git clone https://github.com/aotabekov91/plugin 
run git clone https://github.com/aotabekov91/umay 

run cd /code/plugin && pip install -r requirements.txt -e .
run cd /code/umay  && pip install -r requirements.txt -e .
