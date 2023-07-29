from plugin import Plug

from .parser import SnipsParser

class Umay(Plug):

    def __init__(self):

        super(Umay, self).__init__()

        self.modes={}
        self.parser=SnipsParser()

    def add(self, mode, port, paths):

        self.modes[mode]=port
        self.parser.add(paths)

    def parse(self, text, mode, prob=0.5):

        r=self.parser.parse(text, mode)
        return {'status':'ok', 'info': 'parsed', 'result': r}
