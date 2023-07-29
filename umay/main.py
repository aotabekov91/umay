from plugin import Plug
from .parser import SnipsParser

class Umay(Plug):

    def __init__(self):

        super(Umay, self).__init__()

        self.modes={}
        self.parser=SnipsParser()

    def register(self, mode, port, files):

        self.modes[mode]=port
        self.parser.add(files)

    def parse(self, text, mode=None, prob=0.5):

        r=self.parser.parse(text, mode)
        print({'status':'ok', 'info': 'parsed', 'result': r})
