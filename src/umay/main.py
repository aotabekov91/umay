from plug import Plug
from queue import Queue
from threading import Thread

from .mode import Generic, UmayManager

class Umay(Plug):

    def __init__(self):

        super().__init__(respond_port=True)

        self.queue=Queue()
        self.generic=Generic()
        self.manager=UmayManager(self)

    def setConnection(self):

        super().setConnection(kind='REP')

        if self.parser_port:

            self.parser_socket = self.getConnection(kind='REQ')
            self.parser_socket.connect(
                    f'tcp://localhost:{self.parser_port}')

    def run(self):

        self.running=True

        def listen_queue():

            while self.running:

                data=self.queue.get()
                self.parser_socket.send_json(data)
                respond=self.parser_socket.recv_json()
                print('Received from parser: ', respond) 
                self.manager.act(respond)

        t=Thread(target=listen_queue)
        t.daemon=True
        t.start()

        super().run()

    def register(self, mode, keyword, port, paths):

        self.manager.register(mode, keyword, port)

        if any(paths):

            data={'action':'add', 'mode':mode, 'paths':paths}
            self.parser_socket.send_json(data)
            respond=self.parser_socket.recv_json()
            print(respond)

    def getModes(self): raise

    def parse(self, text, mode=None, prob=0.5, count=1):

        data={'text':text,
              'mode':mode,
              'prob':prob,
              'count':count,
              'action':'parse',
              }

        self.queue.put(data)

def main():

    app=Umay()
    app.run()
