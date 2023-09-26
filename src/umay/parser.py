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

        raise
        if self.parser_port:
            raise
            self.port=self.parser_port
            super().setup()

    def run(self):

        self.connect.set(kind='REP')
        self.connect.run()

    def add(self, mode, paths): 

        if not mode in self.modes: 
            self.modes[mode]=[]

        mode_intents=[]
        mode_entities=[]

        for doc in paths:
            if doc:
                for block in doc:
                    block_type = block.get("type")

                    if block_type == "entity":
                        mode_entities.append(
                                Entity.from_yaml(block))
                    elif block_type == "intent":
                        mode_intents.append(
                                Intent.from_yaml(block))

        for intent in mode_intents:
            self.modes[mode]+=[intent.intent_name]

        self.intents+=mode_intents
        self.entities+=mode_entities
        self.fit()

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)

    def parse(self, text, mode=None, prob=.5, count=1):

        intents=self.modes.get(mode, None)
        return self.engine.parse(
                text, intents=intents)

def run():

    parser=Parser()
    parser.run()
