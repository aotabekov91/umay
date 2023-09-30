from plug.plugs.handler import Handler

from .parser import Parser

class UmayDeamon(Handler):

    def __init__(self): 

        self.modes=[]
        self.sockets={}
        self.keywords={}
        self.prev=None
        self.current=None
        self.umay_port=None
        super(UmayDeamon, self).__init__()

    def setup(self):

        super().setup()
        self.parser=Parser(self)
        self.setConnect(self.umay_port)

    def register(self, data):

        raise
        for mode, d in data.items():

            port=d.get('port', None)
            paths=d.get('paths', [])
            kind=d.get('kind', 'PUSH')
            keyword=d.get('keyword', None)
            
        self.modes+=[mode]
        if keyword:
            self.keywords[keyword]=mode
        if port:
            socket=self.connect.get(kind)
            socket.connect(
                    f'tcp://localhost:{port}')
            self.sockets[mode]=(socket, kind)
        print(mode, port, paths)
        # if any(paths):
            # self.parser.add(mode, paths)

    def parse(self, **kwargs):

        self.parser.serve(**kwargs)

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
