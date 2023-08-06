import argparse

from plug import Plug

class UmayCLI(Plug):

    def setConnection(self, initial=True): 

        if not initial:

            self.socket = self.getConnection('REQ')
            self.socket.connect(f'tcp://localhost:{self.port}')

    def setSettings(self):

        super().setSettings()

        self.parser=argparse.ArgumentParser()

        self.subparser=self.parser.add_subparsers(dest='command')
        self.subparser.add_parser('exit')

        self.parser_action=self.subparser.add_parser('parse')
        self.parser_action.add_argument('-m', '--mode')
        self.parser_action.add_argument('-t', '--text')
        self.parser_action.add_argument('-p', '--prob')

    def runAction(self, action, request={}):

        self.setConnection(initial=False)

        request['action']=action
        self.socket.send_json(request)
        respond=self.socket.recv_json()
        return respond

    def run(self):

        args = self.parser.parse_args()

        if args.command=='parse':
            self.runAction('parse', vars(args))
        elif args.command=='exit':
            self.runAction('exit')

def main():

    cli = UmayCLI()
    cli.run()
