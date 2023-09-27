from queue import Queue
from threading import Thread
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

        self.prev=None
        self.current=None
        self.parser=None
        self.queue=Queue()
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
            self.parser = self.connect.get(
                    kind='REQ')
            self.parser.connect(
                    f'tcp://localhost:{self.parser_port}')

    def runListen(self):
        pass

    def runQueue(self):

        def run():
            while self.running:
                req=self.queue.get()
                print(f'Umay sending to parser: {req}')
                self.parser.send_json(
                        {'parse': req})
                res=self.parser.recv_json()
                self.act(res.get('parse', None))

        if self.parser:
            self.running=True
            thread=Thread(target=run)
            thread.daemon=True
            thread.start()
            return thread

    def run(self):

        self.runQueue()
        self.runListen()
        super().run()

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
            respond=self.parser.recv_json()
            print(respond)

    def parse(self, **kwargs):
        self.queue.put(kwargs)

    def getAction(self, respond):

        result=respond.get('result', {})
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

    def setMode(
            self, 
            mode=None, 
            keyword=None): 

        if keyword:
            mode=self.keywords.get(
                    keyword, None)
        if mode: 
            self.current=mode

    def act(self, respond):

        action=None
        if respond:
            action=self.getAction(respond)
        if action:
            m, r = action
            if m!='Generic': 
                self.setMode(mode=m)
            con=self.sockets.get(
                    self.current, None)
            if con:
                socket, kind= con
                socket.send_json(r)

def run():

    app=Umay()
    app.run()
