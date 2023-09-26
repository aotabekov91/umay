from ubuntu:20.04

expose 20001
workdir /code

run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
# && apt install -y python3-poetry
run git clone https://github.com/aotabekov91/umay && cd umay
# run cd umay && poetry install --extras parser
# run poetry shell
# run pip install snips_nlu && python -m snips_nlu download en

# cmd ["umayp"]
