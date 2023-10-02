from threading import Thread

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

from plug.plugs.handler import Handler

class Parser(Handler):

    def __init__(self, lan='en'):

        self.lan=lan
        self.modes={}
        self.intents=[]
        self.entities=[]
        self.engine=SnipsNLUEngine()
        super().__init__()

    def setup(self):

        super().setup()
        self.setConnect(
                kind='REP',
                socket_kind='bind',
                port=self.parser_port)

    def parse(self, 
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
        return {'status':'ok'}

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)
        return {'status': 'ok'}

    def handle(self, req):

        r=super().handle(req)
        print(r)
        self.connect.socket.send_json(r)

def run():

    parser=Parser()
    parser.run()
