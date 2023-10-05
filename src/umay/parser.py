from threading import Thread

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

from plug.plugs.handler import Handler

class Parser(Handler):

    def __init__(self, lan='en'):

        self.apps={}
        self.lan=lan
        self.intents=[]
        self.entities=[]
        self.mode_keys={}
        self.app_keys=set()
        self.keywords={}
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
              app=None, 
              mode=None,
              ):

        intents=None
        if app:
            intents=self.apps.get(
                    app, None)
            if mode:
                intents=intents[mode]
            else:
                intents=list(intents.items())
        return self.engine.parse(
                text, intents=intents)

    def register(self, app, units, keywords): 

        if not app in self.apps: 
            self.apps[app]={}
            self.keywords[keywords]=set()
            for n, us in units.items():
                for i in us:
                    unit=i['unit']
                    self.keywords[keywords].add(
                            i['keywords'])
                    if unit.get("type") == "entity":
                        l=Entity.from_yaml(unit)
                        self.entities.append(l)
                    elif unit.get("type") == "intent":
                        l=Intent.from_yaml(unit)
                        self.intents.append(l)
                        self.apps[app][n]=l
            self.updateKeywordEntities()
        return {'status':'ok'}

    def getKeywords(self):

        return {
                'status': 'ok', 
                'keywords': self.keywords
               }

    def updateKeywordEntities(self):

        app_ent={
                'name': 'app', 
                'type': 'entity', 
                'values': list(self.keywords.keys()),
                'automatically_extensible': False}
        mode_ent={
                'name': 'mode',
                'type': 'entity', 
                'values': list(self.keywords.values()),
                'automatically_extensible': False}
        m=Entity.from_yaml(app_ent)
        p=Entity.from_yaml(mode_ent)
        self.entities.append(m)
        self.entities.append(p)

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)
        print('Fitted dataset')
        return {'status': 'ok', 'action': 'fitted'}

    def handle(self, req):

        r=super().handle(req)
        self.connect.socket.send_json(r)

def run():

    parser=Parser()
    parser.run()
