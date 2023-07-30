import zmq
from plug import Plug
from queue import Queue
from threading import Thread

class Umay(Plug):

    def __init__(self):

        super(Umay, self).__init__()

        self.modes={}
        self.queue=Queue()

    def setConnection(self):

        super().setConnection()

        if self.parser_port:
            self.psocket = zmq.Context().socket(zmq.REQ)
            self.psocket.connect(f'tcp://localhost:{self.parser_port}')

    def run(self):

        self.running=True

        def listen_queue():

            while self.running:

                data=self.queue.get()
                self.psocket.send_json(data)
                respond=self.psocket.recv_json()
                print(respond)

        t=Thread(target=listen_queue)
        t.daemon=True
        t.start()

        super().run()

    def register(self, mode, port, paths):

        self.modes[mode]=port
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
