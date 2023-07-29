from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

from snips_nlu.dataset.entity import Entity
from snips_nlu.dataset.intent import Intent

from snips_nlu.dataset.yaml_wrapper import yaml

class SnipsParser(SnipsNLUEngine):

    def __init__(self):

        super(SnipsParser, self).__init__()

        self.docs=[]
        self.modes={}

    def add(self, paths): 

        self.docs+=paths
        self.fit()

    def fit(self):

        entities=[]
        intents=[]

        for doc in self.docs:
            for block in doc:
                block_type = block.get("type")
                if block_type == "entity":
                    entities.append(Entity.from_yaml(block))
                elif block_type == "intent":
                    intents.append(Intent.from_yaml(block))

        self.dataset = Dataset('en', intents, entities)

        super().fit(self.dataset.json)

        for intent in self.dataset.intents:
            mode=intent.intent_name.split('_')[0]
            if not mode in self.modes: self.modes[mode]=[]
            self.modes[mode]+=[intent.intent_name]

    def parse(self, text, mode=None, prob=.5):

        def get_slot_names(data):
            slots={}
            for s in data['slots']: 
                slots[s['slotName']]=s['value']['value']
            return slots

        intents=self.modes.get(mode, None)

        i_data=super().parse(text, intents=intents)
        c_name=i_data['intent'].get('intentName', None)

        if c_name:
            m_name = c_name.split('_')[0]
            i_prob=i_data['intent']['probability']
            if prob<i_prob:
                s_names=get_slot_names(i_data)
                return m_name, c_name, s_names, i_data, i_prob

        return None, None, {}, i_data, 0
