from snips_nlu 

# from ubuntu
expose 19999
expose 20001
# workdir /code
# run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
## copy requirements.txt requirements.txt
# run pip install -r requirements.txt
# run git clone https://github.com/aotabekov91/umay
# run cd umay && pip install .
# cmd umayp

run rm -rf umay;  git clone https://github.com/aotabekov91/umay
# run cd umay && pip install  .
