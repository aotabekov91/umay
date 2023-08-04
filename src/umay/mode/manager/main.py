import zmq 
from plug import Plug

class UmayManager(Plug): 

    def __init__(self, umay): 

        self.sockets={}
        self.modes={}
        self.mode=None
        self.umay=umay

        super().__init__()

    def setModeConnection(self, port, kind):

        socket=zmq.Context().socket(kind)
        socket.connect(f'tcp://localhost:{port}')
        return socket

    def register(self, mode, keyword, port, kind=zmq.PUSH): 

        if port:
            self.sockets[mode]=self.setModeConnection(port, kind)
            self.modes[keyword]=mode

    def setMode(self, keyword): 

        mode=self.modes.get(keyword, None)
        if mode: self.mode=mode
        print('Umay mode: ', self.mode) 

    def act(self, respond):

        todo=self.parse(respond)
        print('Umay to do: ', todo)

        if todo:

            mode, request = todo

            if mode==self.name:
                self.handle(request)
            else:
                if mode!='Generic': self.mode=mode
                socket=self.sockets.get(self.mode, None)
                if socket: socket.send_json(request)

    def parse(self, respond):

        result=respond.get('result', None)

        if result: 

            intent=result.get('intent')
            slots=result.get('slots')

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
