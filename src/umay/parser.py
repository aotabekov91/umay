from queue import Queue
from threading import Thread

# from snips_nlu import SnipsNLUEngine
# from snips_nlu.dataset import Dataset
# from snips_nlu.dataset.entity import Entity
# from snips_nlu.dataset.intent import Intent

class Parser:

    def __init__(
            self, 
            handler,
            lan='en'):

        self.lan=lan
        self.modes={}
        self.intents=[]
        self.entities=[]
        self.queue=Queue()
        self.handler=handler
        # self.engine=SnipsNLUEngine()

    def run(self):

        def listen():
            while self.handler.running:
                data=self.queue.get()
                result=self.parse(**data)
                self.handler.act(result)

        thread=Thread(target=listen)
        thread.deamon=True
        thread.start()
        return thread

    def serve(self, **kwargs):
        self.queue.put(kwargs)

    def add(self, mode, paths): 

        if not mode in self.modes: 
            self.modes[mode]=[]
        i, e = [], []
        for doc in paths:
            if doc:
                for b in doc:
                    btype = b.get("type")
                    if btype == "entity":
                        e.append(Entity.from_yaml(b))
                    elif btype == "intent":
                        i.append(Intent.from_yaml(b))
        for p in i:
            self.modes[mode]+=[p.intent_name]
        self.intents+=i
        self.entities+=e
        self.fit()

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)

    def parse(self, 
              text, 
              prob=.5, 
              count=1,
              mode=None, 
              ):

        mintents=self.modes.get(mode, None)
        return self.engine.parse(
                text, 
                intents=mintents)
