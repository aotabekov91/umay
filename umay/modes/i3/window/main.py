import os
import asyncio

from willmann import GenericMode, command

class WindowsMode(GenericMode):

    @command()
    def hintJump(self):

        self.activateInput('setTextInitials')
        return 'i3-easyfocus -a'

    @command(finishCheck=True, windowCheck=True)
    def focus(self, request):

        slot_names=request.get('slot_names', {})
        window=slot_names.get('direction', None)
        if window in ['tiling', 'floating']:
            return 'focus mode_toggle'
        elif window in ['left', 'right']:
            workspaces=asyncio.run(self.manager.get_workspaces())
            for w in workspaces:
                if not w.visible: continue
                if window=='left' and w.num%2==0:
                    return f'workspace {w.num}'
                elif window=='right' and w.num%2==1:
                    return f'workspace {w.num}'

    @command(finishCheck=True, windowCheck=True)
    def changeWorkspace(self, request):

        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            return f'workspace {int(workspace)}'

    @command(finishCheck=True, windowCheck=True)
    def moveToWorkspace(self, request):

        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            return f'move container to workspace {workspace}; workspace {int(workspace)}'

    @command(windowCheck=True)
    def floatingToggle(self):

        return 'floating toggle'

    @command(finishCheck=True, windowCheck=True)
    def hide(self):

        return 'move scratchpad'

    @command(finishCheck=True, windowCheck=True, wait=0.1)
    def close(self):

        return 'kill'

if __name__=='__main__':
    app=WindowsMode(port=8234)
    app.run()
