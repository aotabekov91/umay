from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

class SnipsParser(SnipsNLUEngine):

    def __init__(self, lan='en'):

        super(Parser, self).__init__()

        self.lan=lan
        self.modes={}

    def add(self, mode, file): 

        if not mode in self.modes: self.modes[mode]=[]
        self.modes[mode]+=[file]

    def fit(self):

        self.dataset = Dataset.from_yaml_files(
                language=self.lan, 
                filenames=self.files)

        super().fit(self.dataset.json)

        for intent in self.dataset.intents:
            mode_name=intent.intent_name.split('_')[0]
            if not mode_name in self.modes:
                self.modes[mode_name]=[]
            self.modes[mode_name]+=[intent.intent_name]

    def parse(self, text, mode=None, prob=.5):

        def get_slot_names(data):
            slots={}
            for s in data['slots']: 
                slots[s['slotName']]=s['value']['value']
            return slots

        mode=self.modes.get(mode, None)

        i_data=super().parse(text, intents=intents)
        c_name=i_data['intent'].get('intentName', None)

        if c_name:
            m_name = c_name.split('_')[0]
            i_prob=i_data['intent']['probability']
            if prob<i_prob:
                s_names=get_slot_names(i_data)
                return m_name, c_name, s_names, i_data, i_prob

        return None, None, {}, i_data, 0
