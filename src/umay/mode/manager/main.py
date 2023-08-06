from plug import Plug

class UmayManager(Plug): 

    def __init__(self, umay): 

        self.sockets={}
        self.modes={}
        self.mode=None
        self.umay=umay

        super().__init__()

    def register(self, mode, keyword, port, kind): 

        if port:
            socket=self.getConnection(kind)
            socket.connect(f'tcp://localhost:{port}')
            self.sockets[mode]=(socket, kind)
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

                socket, kind=self.sockets.get(
                        self.mode, (None, None))

                if socket: 
                    socket.send_json(request)
                if kind in ['REQ']:
                    respond=socket.recv_json()
                    print(respond)
                    return respond

    def parse(self, respond):

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
