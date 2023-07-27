import asyncio
import subprocess

# import libtmux
# from i3ipc.aio import Connection

from ..utils import os_command
from .input import InputMode

from plugin.utils import register

class GenericMode(InputMode):

    def __init__(self, 

                 name=None, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 window_classes='all',
                 app_name='own_floating',
                 leader=None,
                 ):

        super(GenericMode, self).__init__(
                 name=name, 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=window_classes,
                 app_name=app_name,
                 leader=leader,
                )

        # self.tmux=libtmux.Server()
        # self.manager=asyncio.run(Connection().connect())

    def change_mode(self, mode=None):

        if mode=='me':
            mode=self.__class__.__name__
        if self.parent_port and mode:
            self.parent_socket.send_json({'command':'setCurrentMode', 'mode':mode})
            respond=self.parent_socket.recv_json()

    def get_current_window(self):

        tree=asyncio.run(self.manager.get_tree())
        return tree.find_focused()

    def get_window_class(self):

        window=self.get_current_window()
        if window.name=='tmux':
            cmd=('list-panes', '-F', '#{pane_id}:#{pane_pid}:#{pane_active}')
            r=self.tmux.cmd(*cmd)
            for pane_data in r.stdout:
                pane_id, pid, active=tuple(pane_data.split(':'))
                if active=='1':
                    cmd=f'ps -o cmd --no-headers --ppid {pid}'.split(' ')
                    w=subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    processes=w.stdout.readlines()
                    if len(processes)>0:
                        process_name=(processes[-1]
                                      .decode()
                                      .strip('\n')
                                      .lower()
                                      )
                        for f in ['vim', 'ranger']:
                            if f in process_name: return f
            return 'tmux'
        else:
            return window.window_class

    def set_repeats(self, request, command):

        slot_names=request.get('slot_names', {})
        repeat=int(slot_names.get('repeat', 1.))
        return command.format(repeat=times)

    def editor(self, slot_names): 

        if self.parent_port:
            slot_names['client']=self.__class__.__name__
            self.parent_socket.send_json({
                    'command': 'setMode',
                    'mode_name' : 'EditorMode',
                    'mode_action': 'activate',
                    'slot_names':slot_names,
                    })
            respond=self.parent_socket.recv_json()

    def check(self):

        if self.parent_port:
            window_class=self.get_window_class()
            self.parent_socket.send_json(
                    {'command':'setCurrentWindow',
                     'window_class': window_class,
                     })
            respond=self.parent_socket.recv_json()

    def lock(self, request):

        self.parent_socket.send_json({
            'command': 'lock',
            'mode_name':self.__class__.__name__,
            'mode_action': 'lockListen',})
        respond=self.parent_socket.recv_json()

    @os_command(finishCheck=True)
    def unlock(self, request):

        self.parent_socket.send_json({
            'command': 'unlock',
            'mode_name':self.__class__.__name__})
        respond=self.parent_socket.recv_json()

    @os_command(finishCheck=True)
    def lockListen(self, request):

        text=request['slot_names']['text']
        slots=request['slot_names']['slots']
        action=request['slot_names']['command']
        if action:
            command=action.split('_')[-1]
            action=getattr(self, command, None)
            if not action and hasattr(self, 'ui'):
                action=getattr(self.ui, command, None)
        if action and 'magic' in text:
            action({'slot_names':slots})
        else:
            text=text.replace(' ', '" "').strip()
            return f'xdotool getactivewindow type {text}" "'

    @os_command(finishCheck=True)
    def confirm(self, request):

        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @os_command()
    def cancel(self, request):

        return 'xdotool getactivewindow key --repeat {repeat} Escape'

    @os_command()
    def forward(self, request):

        return self.set_repeats(request, 'xdotool getactivewindow key --repeat {repeat} ctrl+f')

    @os_command()
    def backward(self, request):

        return self.set_repeats(request, 'xdotool getactivewindow key --repeat {repeat} ctrl+b')

    @os_command()
    def next(self, request):

        return self.set_repeats(request, 'xdotool getactivewindow key --repeat {repeat} space')

    @os_command()
    def previous(self, request):

        return self.set_repeats(request, 
                                'xdotool getactivewindow key --repeat {repeat} shift+space')

    @os_command(commandType='i3')
    def fullscreen(self, request):

        return 'fullscreen toggle'
    
    @os_command()
    def zoomIn(self, request):

        return self.set_repeats(request, 'xdotool getactivewindow key --repeat {repeat} plus')

    @os_command()
    def zoomOut(self, request):

        return self.set_repeats(request, 'xdotool getactivewindow key --repeat {repeat} minus')

    def changeMode(self, request):

        slot_names=request['slot_names']
        mode_name=slot_names.get('mode', None)
        if mode_name: self.change_mode(mode_name)

    @os_command(finishCheck=True)
    def escape(self, request):

        super().escape(request)
        self.unlock(request)

    @register('h')
    def hide(self):

        if hasattr(self, 'ui'):
            self.ui.hide()

    @register('q')
    def exit(self):

        super().exit()

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()
