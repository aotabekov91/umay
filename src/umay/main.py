from plug.plugs.handler import Handler

class UmayDeamon(Handler):

    def __init__(self): 

        self.prev=None
        self.current=None
        self.umay_port=None
        self.sockets={}
        self.keywords={}
        super(UmayDeamon, self).__init__()

    def setup(self):

        super().setup()
        self.setConnect(
                socket_kind='bind',
                port=self.umay_port
                )
        self.setParserConnect()

    def setParserConnect(self):

        self.psocket=self.connect.get('REQ')
        self.psocket.connect(
                f'tcp://localhost:{self.parser_port}')

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
            self.sockets[name]=(socket, kind, port)
        if units:
            cmd={'register':{'mode':name, 'units':units}}
            self.psocket.send_json(cmd)
            res=self.psocket.recv_json()
            print(res)
            self.fit()

    def fit(self):

        self.psocket.send_json({'fit':{}})
        res=self.psocket.recv_json()
        print(res)

    def parse(self, **kwargs):

        cmd={'parse':kwargs}
        self.psocket.send_json(cmd)
        res=self.psocket.recv_json()
        print(res)
        self.act(res['parse'])

    def getAction(self, result):

        intent=result.get('intent', {})
        slots=result.get('slots', [])
        iname=intent.get('intentName', None)
        if iname:
            req={}
            d=iname.split('_', 1)
            mode, action = d[0], d[1]
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
                socket, kind, port = con
                print('Connection: ', con)
                socket.send_json(r)
        print(action, self.current)
        print(self.sockets)

    def run(self):

        self.running=True
        super().run()

def run():

    app=UmayDeamon()
    app.run()
