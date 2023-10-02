from queue import Queue
from threading import Thread

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

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
        self.engine=SnipsNLUEngine()

    def run(self):

        def listen():
            while self.handler.running:
                data=self.queue.get()
                result=self._parse(**data)
                self.handler.act(result)

        thread=Thread(target=listen)
        thread.deamon=True
        thread.start()
        return thread

    def parse(self, **kwargs):
        self.queue.put(kwargs)

    def _parse(self, 
              text, 
              prob=.5, 
              count=1,
              mode=None, 
              plug=None,
              ):

        intents=None
        if mode:
            mode_intents=self.modes.get(mode, None)
            if plug:
                intents=mode_intents[plug]
            else:
                intents=list(mode_intents.items())
        return self.engine.parse(
                text, 
                intents=intents)

    def register(self, mode, units): 

        if not mode in self.modes: 
            self.modes[mode]={}
            for n, us in units.items():
                for u in us:
                    if u.get("type") == "entity":
                        l=Entity.from_yaml(u)
                        self.entities.append(l)
                    elif u.get("type") == "intent":
                        l=Intent.from_yaml(u)
                        self.intents.append(l)
                        self.modes[mode][n]=l

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)
