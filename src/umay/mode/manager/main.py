import zmq 
from plug import Plug

class Manager(Plug): 

    def __init__(self, umay): 

        self.modes={}
        self.mode=None
        self.umay=umay

        super().__init__()

    def setModeConnection(self, port, kind):

        socket=zmq.Context().socket()
        socket.connect(f'tcp://localhost:{port}')
        return socket

    def register(self, mode, port, kind=zmq.PUSH): 

        self.modes[mode]=self.setSocket(port, kind)

    def setMode(self, mode): self.mode=mode

    def act(self, respond):

        todo=self.parse(respond)

        if todo:
            mode, requst = todo
            if mode!='Generic': self.mode=mode
            socket=self.modes.get(self.mode, None)
            if socket: socket.send_json(requst)

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
