# from ubuntu:20.04
# expose 19999
# workdir /code/umay
# run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
# run pip install snips_nlu

from ready
copy . . 
run pip install .
cmd ["umayd"]
