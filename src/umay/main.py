from plug.plugs.handler import Handler

from .parser import Parser

class UmayDeamon(Handler):

    def __init__(self): 

        self.sockets={}
        self.keywords={}
        self.prev=None
        self.current=None
        self.umay_port=None
        super(UmayDeamon, self).__init__()
        self.parser=Parser(self)

    def setup(self):

        super().setup()
        self.setConnect(
                socket_kind='bind',
                port=self.umay_port
                )

    def register(
            self, 
            name=None,
            port=None,
            kind='PUSH',
            units=[]):

        if port:
            socket=self.connect.get(kind)
            socket.connect(
                    f'tcp://localhost:{port}')
            self.sockets[name]=(socket, kind)
        if units:
            self.parser.register(name, units)
            self.parser.fit()

    def parse(self, **kwargs):
        self.parser.parse(**kwargs)

    def getAction(self, result):

        intent=result.get('intent', {})
        slots=result.get('slots', {})
        iname=intent.get('intentName', None)
        if iname:
            nm=iname.split('_', 1)
            if len(nm)==2:
                req={}
                mode, action = nm[0], nm[1]
                for s in slots:
                    v=s['value']['value']
                    req[s['slotName']]=v
                return mode, {action: req}

    def act(self, result):

        action=self.getAction(result)
        if action:
            m, r = action
            if m!='Generic': 
                self.current=m
            con=self.sockets.get(
                    self.current, None)
            if con:
                socket, kind= con
                socket.send_json(r)

    def run(self):

        self.running=True
        self.parser.run()
        super().run()

def run():

    app=UmayDeamon()
    app.run()
