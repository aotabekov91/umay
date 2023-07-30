import zmq
from plug import Plug

class Parser(Plug):

    def __init__(self):

        super(Parser, self).__init__()

        self.modes={}
        self.intents=[]
        self.entities=[]

    def setConnection(self): 

        if self.parser_port:
            self.socket = zmq.Context().socket(zmq.REP)
            self.socket.bind(f'tcp://*:{self.parser_port}')

    def add(self, mode, paths):  pass

    def fit(self):  pass

    def parse(self, text, mode=None, prob=.5, count=1): pass

    def run(self): super().run(answer=True)

def main():

    parser=Parser()
    parser.run()
