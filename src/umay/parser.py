from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

class Parser(SnipsNLUEngine):

    def __init__(self, lan='en'):

        self.lan=lan
        self.apps={}
        self.units={}
        self.keywords={}
        super().__init__()

    def register(self, 
                 app, 
                 units, 
                 app_keys,
                 mode_keys): 

        self.apps[app]={}
        self.units[app]=units
        self.keywords[app] = {
                'app': app_keys, 
                'mode': mode_keys
                }
        i, e = self.setUnits()
        self.fit(intents=i, entities=e)
        return {
                'status':'ok', 
                'info': f'Umay registred {app}'
               }

    def setUnits(self):

        keys=[]
        intents=[]
        entities=[]
        for app, units in self.units.items():
            for n, us in units.items():
                for i in us:
                    if i.get('type') == "entity":
                        if i.get('name') in ['app', 'mode']:
                            keys+=[i]
                        else:
                            l=Entity.from_yaml(i)
                            entities.append(l)
                    elif i.get('type') == "intent":
                        l=Intent.from_yaml(i)
                        intents.append(l)
                        self.apps[app][n]=l
        entities+=self.updateKeys(keys)
        return intents, entities

    def updateKeys(self, keys):

        entities=[]
        for e in keys:
            if e.get('name')=='app':
                values=[]
                for n, app in self.keywords.items():
                    values+=[app['app']]
                e['values']=values
            elif e.get('name')=='mode':
                values=[]
                for n, app in self.keywords.items():
                    values+=app['mode']
                e['values']=values
            l=Entity.from_yaml(e)
            entities.append(l)
        return entities

    def fit(self, 
            intents=[], 
            entities=[]
            ): 

        data = Dataset(
                self.lan, 
                intents, 
                entities)
        super().fit(data.json)
        return {
                'status': 'ok', 
                'action': 'fitted'
               }
