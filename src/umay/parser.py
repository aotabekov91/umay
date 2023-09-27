from plug.plugs.handler import Handler

# from snips_nlu import SnipsNLUEngine
# from snips_nlu.dataset import Dataset
# from snips_nlu.dataset.entity import Entity
# from snips_nlu.dataset.intent import Intent

class Parser(Handler):

    def __init__(
            self, 
            *args, 
            lan='en',
            parser_port=None,
            **kwargs):

        self.lan=lan
        self.modes={}
        self.intents=[]
        self.entities=[]
        self.parser_port=parser_port
        
        super(Parser, self).__init__(
                *args, **kwargs)

        # self.engine=SnipsNLUEngine()

    def setup(self):

        super().setup()
        self.setConnect(
                port=self.parser_port,
                kind='REP')

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
              mode=None, 
              prob=.5, 
              count=1):

        i=self.modes.get(mode, None)
        return self.engine.parse(
                text, intents=i)

def run():

    parser=Parser()
    parser.run()
