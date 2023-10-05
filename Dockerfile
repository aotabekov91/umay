from ubuntu:20.04
workdir /code/umay
run apt update && apt install -y python3 && apt install -y python3-pip && apt install -y git
copy . . 
run pip install "../umay[daemon]"
cmd ["umayd"]
