from ubuntu:20.04

expose 20001
workdir /code

run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
run git clone https://github.com/aotabekov91/umay
run pip install 'umay[parser]'
run pip install snips_nlu && python3 -m snips_nlu download en

# cmd ["umayp"]
