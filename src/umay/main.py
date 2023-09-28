from plug.plugs.generic import Generic
from plug.plugs.handler import Handler

class Umay(Handler):

    def __init__(self, 
                 *args, 
                 parser_port=None,
                 handler_port=None,
                 **kwargs):

        self.modes=[]
        self.sockets={}
        self.keywords={}
        self.parser=None
        self.prev=None
        self.current=None
        self.generic=Generic()
        self.parser_port=parser_port
        self.handler_port=handler_port

        super(Umay, self).__init__(
                *args,
                **kwargs
                )

    def setup(self):

        super().setup()
        self.setConnect(self.handler_port)
        self.setParserConnect()

    def setParserConnect(self):

        if self.parser_port:
            self.parser = self.connect.get('PUSH')
            self.parser.connect(
                    f'tcp://localhost:{self.parser_port}')

    def register(self, 
                 mode, 
                 port, 
                 paths=[],
                 kind='PUSH',
                 keyword=None, 
                 **kwargs,
                 ):

        self.modes+=[mode]
        if keyword:
            self.keywords[keyword]=mode
        if port:
            socket=self.connect.get(kind)
            socket.connect(
                    f'tcp://localhost:{port}')
            self.sockets[mode]=(socket, kind)
        if any(paths):
            data={'mode':mode, 'paths':paths}
            self.parser.send_json({'add': data})

    def parse(self, **kwargs):

        self.parser.send_json(
                {'parse': kwargs})

    def getAction(self, result):

        intent=result.get('intent', {})
        slots=result.get('slots', {})
        iname=intent.get('intentName', None)

        if iname:
            nm=iname.split('_', 1)
            if len(nm)==2:
                mode, action = nm[0], nm[1]
                req={}
                for s in slots:
                    v=s['value']['value']
                    req[s['slotName']]=v
                return mode, {action: req}

    def act(self, **kwargs):

        action=self.getAction(**kwargs)
        if action:
            m, r = action
            if m!='Generic': 
                self.current=m
            con=self.sockets.get(
                    self.current, None)
            if con:
                socket, kind= con
                socket.send_json(r)

def run():

    app=Umay()
    app.run()
