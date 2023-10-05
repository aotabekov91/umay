from queue import Queue
from threading import Thread

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent
from snips_nlu.cli.download import download

class Parser:

    def __init__(self, daemon, lan='en'):

        self.apps={}
        self.lan=lan
        self.intents=[]
        self.entities=[]
        self.keywords={}
        self.queue=Queue()
        self.daemon=daemon
        self.downloadLan(lan)
        self.engine=SnipsNLUEngine()
        self.listen()

    def downloadLan(self, lan):
        download(lan)

    def listen(self):

        def run():
            self.listening=True
            while self.listening:
                text, cand = self.queue.get()
                parsed=self.engine.parse(
                        text, intents=cand)
                self.act(parsed)

        thread=Thread(target=run)
        thread.daemon=True
        thread.start()
        return thread
    
    def parse(self, 
              text, 
              prob=.5, 
              count=1,
              app=None, 
              mode=None,
              ):

        cand=self.apps.get(
                app, None)
        if cand:
            cand=cand.get(
                    mode, 
                    list(cand.items()))
        self.queue.put((text, cand))
        return {'status': 'ok', 
                'info': f'received to parse {text}'}

    def act(self, parsed):

        action=self.simplify(parsed)
        if action:
            app, req = action
            self.daemon.act(app, req)

    def simplify(self, result):

        intent=result.get('intent', {})
        slots=result.get('slots', [])
        iname=intent.get('intentName', None)
        if iname:
            req={}
            d=iname.split('_', 1)
            app, action = d[0], d[1]
            for s in slots:
                v=s['value']['value']
                req[s['slotName']]=v
            return app, {action: req}

    def register(self, 
                 app, 
                 units, 
                 app_keys,
                 mode_keys): 

        if not app in self.apps: 
            self.apps[app]={}
            self.keywords[app] = {
                    'app': app_keys, 
                    'mode': mode_keys}
            for n, us in units.items():
                for i in us:
                    if i.get('type') == "entity":
                        l=Entity.from_yaml(i)
                        self.entities.append(l)
                    elif i.get('type') == "intent":
                        l=Intent.from_yaml(i)
                        self.intents.append(l)
                        self.apps[app][n]=l
            self.update(app)
            self.fit()
        return {'status':'ok', 'info': f'Umay registred {app}'}

    def update(self, app):

        akeys=self.keywords[app]['app']
        mkeys=self.keywords[app]['mode']
        for i in [akeys, mkeys]:
            ent={'name': 'app', 
                 'type': 'entity', 
                 'values': i,
                 'automatically_extensible': False}
            m=Entity.from_yaml(ent)
            if not m in self.entities:
                self.entities.append(m)

    def fit(self): 

        self.dataset = Dataset(
                self.lan, 
                self.intents, 
                self.entities)
        self.engine.fit(self.dataset.json)
        return {'status': 'ok', 'action': 'fitted'}

    def getKeywords(self):

        return {'status': 'ok', 
                'keywords': self.keywords}
