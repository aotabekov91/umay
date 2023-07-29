import zmq
import json
import argparse

from plug import Plug

from .main import Umay

class UmayCLI(Plug):

    def setConnection(self): pass

    def setSettings(self):

        super().setSettings()

        self.parser=argparse.ArgumentParser()

        self.subparser=self.parser.add_subparsers(dest='command')

        self.subparser.add_parser('exit')
        self.parser_action=self.subparser.add_parser('parse')

        self.parser_action.add_argument('-m', '--mode')
        self.parser_action.add_argument('-t', '--text')
        self.parser_action.add_argument('-p', '--prob')

    def setSocket(self): 

        self.socket = zmq.Context().socket(zmq.PUSH)
        self.socket.connect(f'tcp://localhost:{self.port}')

    def runAction(self, action, request={}):

        self.setSocket()

        request['action']=action
        self.socket.send_json(request)
        if action!='exit':
            response=self.socket.recv_json()
            json_object = json.dumps(response, indent = 4) 
            print(json_object)

    def runApp(self):

        app=Umay()
        self.setSocket()

        if app.socket:
            app.run()
        else:
            print('An instance of Willmann is already running')

    def run(self):

        args = self.parser.parse_args()

        if args.command=='parse':
            self.runAction('parse', vars(args))
        elif args.command=='exit':
            self.runAction('exit')
        elif args.command is None:
            self.runApp()

if __name__=='__main__':

    cli = UmayCLI()
    cli.run()
