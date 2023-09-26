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

        self.modes={}
        self.sockets={}
        self.prev=None
        self.parser=None
        self.current=None
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
        self.connect.set()
        self.setParserConnect()

    def setParserConnect(self):

        if self.parser_port:
            self.parser = self.connect.get(kind='REQ')
            port=f'tcp://localhost:{self.parser_port}'
            self.parser.connect(port)

    def listen(self):

        def run():
            while self.running:
                req=self.queue.get()
                self.parser.send_json(req)
                res=self.parser.recv_json()
                self.act(res)
                print('Received from parser: ', res) 

        if self.parser:
            self.running=True
            t=Thread(target=run)
            t.daemon=True
            t.start()

    def run(self):

        self.listen()
        self.connect.run()

    def register(self, 
                 mode, 
                 keyword, 
                 port, 
                 paths,
                 kind,
                 **kwargs,
                 ):

        self.modes[keyword]=mode

        if port:
            socket=self.connect.get(kind)
            socket.connect(f'tcp://localhost:{port}')
            self.sockets[mode]=(socket, kind)

        if any(paths):
            data={'action':'add', 'mode':mode, 'paths':paths}
            self.parser.send_json(data)
            respond=self.parser.recv_json()
            print(respond)

    def parse(self, 
              text, 
              mode=None, 
              prob=0.5, 
              count=1):

        data={'text':text,
              'mode':mode,
              'prob':prob,
              'count':count,
              'action':'parse',
              }
        self.queue.put(data)

    def m_parse(self, respond):

        result=respond.get('result', {})
        intent=result.get('intent', {})
        slots=result.get('slots', {})
        intent_name=intent.get('intentName', None)

        if intent_name:
            nm=intent_name.split('_', 1)
            if len(nm)==2:
                req={}
                mode, action = nm[0], nm[1]
                req={'action': action}
                for s in slots:
                    value=s['value']['value']
                    req[s['slotName']]=value
                return mode, req

    def m_setMode(self, keyword): 

        mode=self.modes.get(keyword, None)
        if mode: 
            self.current=mode
        print('Umay mode: ', self.current) 

    def act(self, respond):

        todo=self.parse(respond)
        print('Umay to do: ', todo)

        if todo:

            mode, request = todo
            if mode==self.name:
                self.handle(request)
            else:
                if mode!='Generic': self.current=mode

                socket, kind=self.sockets.get(
                        self.current, (None, None))

                if socket: 
                    socket.send_json(request)
                if kind in ['REQ']:
                    respond=socket.recv_json()
                    print(respond)
                    return respond

def run():

    app=Umay()
    app.run()
