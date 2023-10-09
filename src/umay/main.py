from queue import Queue
from threading import Thread
from umay.parser import Parser
from plug.plugs.handler import Handler

class Umay(Handler):

    def setup(self):

        super().setup()
        self.setConnect(
                kind='REP', 
                socket_kind='bind', 
                port=self.port)
        self.prev=None
        self.current=None
        self.ports={}
        self.queue=Queue()
        self.connections={}
        self.parser=Parser()

    def simplify(self, result):

        intent=result.get(
                'intent', {})
        slots=result.get(
                'slots', [])
        iname=intent.get(
                'intentName', None)
        if iname:
            req={}
            d=iname.split('_', 1)
            app, action = d[0], d[1]
            for s in slots:
                v=s['value']['value']
                req[s['slotName']]=v
            return app, {action: req}

    def listen(self):

        def run():
            while self.running:
                text, cand = self.queue.get()
                parsed=self.parser.parse(
                        text, intents=cand)
                action=self.simplify(parsed)
                print(action)
                if action:
                    app, req = action
                    self.act(app, req)

        thread=Thread(target=run)
        thread.daemon=True
        thread.start()
        return thread

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
        self.ports[app]=(port, kind)
        self.connections[app]=socket
        return {
                'status': 'ok', 
                'info': f'socketized {app}'
               }

    def fit(self):
        return self.parser.fit()

    def getPorts(self):
        return {
                'status': 'ok', 
                'ports': self.ports
               }

    def getKeywords(self):
        
        return {
                'status': 'ok', 
                'keywords': self.parser.keywords
               }

    def parse(self, 
              text, 
              prob=.5, 
              count=1,
              app=None, 
              mode=None,
              ):
        cand=self.parser.apps.get(
                app, None)
        if cand:
            cand=cand.get(
                    mode, 
                    list(cand.items()))
        self.queue.put((text, cand))
        return {
                'status': 'ok', 
                'info': f'received to parse {text}'
               }
    
    def setState(self, app):

        self.prev=self.current
        self.current =app
        return self.getState()

    def getState(self):

        return {
                'status': 'ok', 
                'prev': self.prev,
                'current': self.current,
               }

    def act(self, app, action):

        s=self.connections.get(
                app, None)
        if s: 
            self.setState(app)
            s.send_json(action)
            return {
                    'status': 'ok', 
                    'info': 'acted'
                   }
        else:
            return {
                    'status': 'nok', 
                    'info': 'socket not found'
                   }

    def run(self):

        self.running=True
        self.listen()
        super().run()

def run():

    app=Umay()
    app.run()
