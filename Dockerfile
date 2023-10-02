from ubuntu:20.04
expose 19999
workdir /code/umay
run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
run pip install 'numpy==1.20'
run pip install snips_nlu
run python3 -m snips_nlu download en

# from ready
copy . . 
run pip install .
# cmd ["umayd"]
