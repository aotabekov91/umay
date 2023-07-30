import zmq
from plug import Plug
from queue import Queue
from threading import Thread

from .mode import Generic, Manager

class Umay(Plug):

    def __init__(self):

        super(Umay, self).__init__()

        self.queue=Queue()
        self.generic=Generic()
        self.manager=Manager(self)

    def setConnection(self):

        super().setConnection()

        if self.parser_port:
            self.psocket = zmq.Context().socket(zmq.REQ)
            self.psocket.connect(
                    f'tcp://localhost:{self.parser_port}')

    def run(self):

        self.running=True

        def listen_queue():

            while self.running:

                data=self.queue.get()
                self.psocket.send_json(data)
                respond=self.psocket.recv_json()
                self.manager.act(respond)

        t=Thread(target=listen_queue)
        t.daemon=True
        t.start()

        super().run()

    def register(self, mode, port, paths):

        self.manager.register(mode, port)
        data={'action':'add', 'mode':mode, 'paths':paths}
        self.psocket.send_json(data)
        respond=self.psocket.recv_json()
        print(respond)

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
