from queue import Queue
from threading import Thread
from plug.plugs.generic import Generic
from plug.plugs.handler import Handler

class Umay(Handler):

    def __init__(self, 
                 *args, 
                 **kwargs):

        super(Umay, self).__init__(
                *args,
                **kwargs
                )

        self.modes={}
        self.sockets={}
        self.current=None
        self.queue=Queue()
        self.generic=Generic()

    def setConnection(self):

        super().setConnection(
                kind='REP')
        if self.parser_port:
            self.parser_socket = self.getConnection(kind='REQ')
            self.parser_socket.connect(
                    f'tcp://localhost:{self.parser_port}')

    def listen(self):

        def _listen():
            while self.running:
                data=self.queue.get()
                self.parser_socket.send_json(data)
                r=self.parser_socket.recv_json()
                print('Received from parser: ', r) 
                self.m_act(r)

        t=Thread(target=_listen)
        t.daemon=True
        t.start()

    def run(self):

        self.running=True
        self.listen()
        self.connect.set(kind='REP')
        self.connect.run()

    def register(self, 
                 mode, 
                 keyword, 
                 port, 
                 paths,
                 kind,
                 **kwargs,
                 ):

        self.m_register(mode, keyword, port, kind)

        if any(paths):
            data={'action':'add', 'mode':mode, 'paths':paths}
            self.parser_socket.send_json(data)
            respond=self.parser_socket.recv_json()
            print(respond)

    def m_register(self, mode, keyword, port, kind): 

        if port:
            socket=self.getConnection(kind)
            socket.connect(f'tcp://localhost:{port}')
            self.sockets[mode]=(socket, kind)
            self.modes[keyword]=mode

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

    def m_act(self, respond):

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
