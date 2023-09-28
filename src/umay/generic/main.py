from plug import Plug
from plug.plugs.umay import Umay

class Generic(Plug):

    def __init__(self,
                 umay_port=None):

        self.umay_port=umay_port
        super().__init__()
        self.umay=Umay(
                umay_port=self.umay_port)
        self.load()

    def load(self):
        self.umay.load([self])
