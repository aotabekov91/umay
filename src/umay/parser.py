import zmq
from plug import Plug

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

class Parser(Plug):

    def __init__(self):

        super(Parser, self).__init__()

        self.modes={}
        self.intents=[]
        self.entities=[]

        self.engine=SnipsNLUEngine()

    def setConnection(self): 

        if self.parser_port:
            self.socket = zmq.Context().socket(zmq.REP)
            self.socket.bind(f'tcp://*:{self.parser_port}')

    def add(self, mode, paths): 

        if not mode in self.modes: self.modes[mode]=[]

        mode_intents=[]
        mode_entities=[]

        for doc in self.docs:
            for block in doc:
                block_type = block.get("type")
                if block_type == "entity":
                    mode_entities.append(Entity.from_yaml(block))
                elif block_type == "intent":
                    mode_intents.append(Intent.from_yaml(block))

        for intent in mode_intents:
            self.modes[mode]+=[intent.intent_name]

        self.intents+=mode_intents
        self.entities+=mode_entities

        self.fit()

    def fit(self): 

        self.dataset = Dataset('en', 
                               self.intents, 
                               self.entities)
        self.engine.fit(self.dataset.json)

    def parse(self, text, mode=None, prob=.5, count=1):

        intents=self.modes.get(mode, None)
        return self.engine.parse(text, intents=intents)

def main():

    parser=Parser()
    parser.run()
