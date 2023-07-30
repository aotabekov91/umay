from plug import Plug

class Manager(Plug): 

    def __init__(self, umay): self.umay=umay

    def act(self, respond):

        result=respond.get('result', None)
        if result: 
            intent=result.get('intent')
            slots=result.get('slots')

            intent_name=intent.get('intent_name', None)

            if intent_name:

                nm=intent_name.split('_', 1)
                if len(nm)==2:
                    mode, action = nm[0], nm[1]

                    print(respond, mode, action)

