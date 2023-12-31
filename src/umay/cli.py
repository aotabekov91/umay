from plug.plugs.cli import CLI
from plug.utils.helpers import pretty_json

class UmayCLI(CLI):

    def setHandlerConnect(self):

        if self.port:
            self.socket=self.connect.get('REQ')
            self.socket.connect(
                    f'tcp://localhost:{self.port}')
        else:
            self.socket=None

    def act(self, action, request={}):

        if self.socket:
            res=self.connect.send(
                    {action: request},
                    self.socket
                    )
            print(pretty_json(res))

def run():
    cli = UmayCLI()
    cli.run()
