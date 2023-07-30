from ubuntu:20.04

expose 20001
workdir /code

run apt update && apt install -y python3.9 && apt install -y python3-pip && apt install -y git
run git clone https://github.com/aotabekov91/plug 
run git clone https://github.com/aotabekov91/umay 
run pip3 install -r requirements.txt "plug" 
run pip3 install -r requirements.txt "umay[snips_nlu]" 
run python3 -m snips_nlu download en
