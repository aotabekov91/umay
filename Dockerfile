from ubuntu:20.04

workdir /code
expose 19999

run apt update && apt install -y python3.9 && apt install -y python3-pip

run apt install -y git

run git clone https://github.com/aotabekov91/plug 
run git clone https://github.com/aotabekov91/umay 

run cd plug && pip3 install -r requirements.txt .
run cd umay && pip3 install -r requirements.txt . 
run python3 -m snips_nlu download en
