from ubuntu:20.04

run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git

expose 20001
workdir /code

run git clone https://github.com/aotabekov91/plug 
run git clone https://github.com/aotabekov91/umay 

run pip3 install "/code/plug"  
run pip3 install "/code/umay[snips_nlu]" 
run python3 -m snips_nlu download en

cmd ["umayp"]
