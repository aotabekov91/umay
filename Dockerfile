from umay:test

expose 20001
workdir /code

run git clone https://github.com/aotabekov91/plug 
run git clone https://github.com/aotabekov91/umay 

run pip install "/code/plug"  
run pip3 install "/code/umay[snips_nlu]" 
run python3 -m snips_nlu download en
