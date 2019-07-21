class Command:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, server, args):
        raise ValueError("execute method not implemented")

class Exit(Command):
    def __init__(self):
        NAME="exit"
        DESCRIPTION="Closes the server"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        server.CloseServer()
