from umay.normal import Normal
from plug.plugs.umay_plug import Umay
from plug.plugs.handler import Handler

class UmayDaemon(Handler):

    def __init__(
            self,
            handler_port=None,
            ): 

        self.sockets={}
        self.current=None
        self.handler_port=handler_port
        super(UmayDaemon, self).__init__()
        self.setDefaultPlugs()

    def setup(self):

        super().setup()
        self.setConnect(
                socket_kind='bind',
                port=self.handler_port)
        self.setParserConnect()
        self.setPlugman()

    def setDefaultPlugs(self):

        default=[Normal, Umay]
        picks=self.plugman.getPicks()
        self.plugman.loadPicks(default+picks)

    def setParserConnect(self):

        self.psocket=self.connect.get('REQ')
        self.psocket.connect(
                f'tcp://localhost:{self.parser_port}')

    def register(
            self, 
            units=[],
            app=None, 
            port=None,
            kind='PUSH',
            keywords=[]):

        if port:
            socket=self.connect.get(kind)
            socket.connect(
                    f'tcp://localhost:{port}')
            self.sockets[app]=(socket, kind, port)
        if units:
            cmd={'register' : {
                        'app' : app, 
                        'units' : units,
                        'keywords': keywords,
                        }
                    }
            self.psocket.send_json(cmd)
            self.psocket.recv_json()
            self.psocket.send_json({'fit':{}})
            self.psocket.recv_json()

    def fit(self):

        self.psocket.send_json(
                {'fit':{}})
        self.psocket.recv_json()

    def parse(self, **kwargs):

        cmd={'parse':kwargs}
        self.psocket.send_json(cmd)
        res=self.psocket.recv_json()
        self.act(res['parse'])

    def getAction(self, result):

        intent=result.get('intent', {})
        slots=result.get('slots', [])
        iname=intent.get('intentName', None)
        if iname:
            req={}
            d=iname.split('_', 1)
            app, action = d[0], d[1]
            for s in slots:
                v=s['value']['value']
                req[s['slotName']]=v
            return app, {action: req}

    def act(self, request):

        action=self.getAction(request)
        if action:
            a, r = action
            self.setAction(a, r)

    def setAction(self, app, action):

        con=self.sockets.get(app, None)
        if con:
            socket, kind, port = con
            socket.send_json(action)

    def handle(self, request):
        super().handle(request)

def run():

    app=UmayDaemon()
    app.run()
