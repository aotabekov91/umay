from umay.parser import Parser
from plug.plugs.handler import Handler

class Daemon(Handler):

    def setup(self):

        super().setup()
        self.setConnect(
                kind='REP', 
                socket_kind='bind', 
                port=self.port)
        self.prev=None
        self.current=None
        self.connections={}
        self.parser=Parser(daemon=self)

    def register(
            self, 
            app, 
            port,
            kind,
            units,
            app_keys,
            mode_keys):

        self.socketize(app, kind, port)
        return self.parser.register(
                app, units, app_keys, mode_keys)

    def socketize(self, app, kind, port):

        socket=self.connect.get(kind)
        socket.connect(
                f'tcp://localhost:{port}')
        self.connections[app]=socket
        return {'status': 'ok', 'info': f'socketized {app}'}

    def fit(self):
        return self.parser.fit()

    def getKeywords(self):
        return self.parser.getKeywords()

    def parse(self, **kwargs):
        return self.parser.parse(**kwargs)
    
    def setState(self, app):

        self.current, self.prev=(app, self.current)
        return self.getState()

    def getState(self):

        data=(self.current, self.prev)
        return {'status': 'ok', 'data': data}

    def act(self, app, action):

        s=self.connections.get(app, None)
        if s: 
            self.setState(app)
            s.send_json(action)
            return {'status': 'ok', 
                    'info': 'acted'}
        else:
            return {'status': 'nok', 
                    'info': 'socket not found'}

def run():

    app=Daemon()
    app.run()
