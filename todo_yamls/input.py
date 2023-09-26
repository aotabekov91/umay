from ..mode import Mode
from ..utils import os_command

class InputMode(Mode):

    @os_command()
    def tab(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Tab'

    @os_command(finishCheck=True)
    def escape(self, request):
        return 'xdotool getactivewindow key Escape'
  
    @os_command(finishCheck=True)
    def enter(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @os_command()
    def space(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @os_command()
    def backspace(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} BackSpace'

    @os_command()
    def interupt(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+c'

    @os_command()
    def copy(self, request):
        return 'xdotool getactivewindow key ctrl+c'

    @os_command()
    def paste(self, request):
        return 'xdotool getactivewindow key ctrl+v'

    @os_command()
    def down(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Down'

    @os_command()
    def up(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Up'

    @os_command()
    def left(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Left'

    @os_command()
    def right(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Right'

if __name__=='__main__':
    app=InputMode(port=33333)
    app.run()
