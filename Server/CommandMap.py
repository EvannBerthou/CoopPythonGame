from Commands import *

class CommandMap:
    def set_commands(self):
        self.register("exit", Exit())
        self.register("quit", Exit())

    def register(self, name, command):
        if name in self.commands:
            print("There is already a command with this name")
            return 0

        self.commands[name] = command

    def execute(self, server, command_name, args):
        if command_name in self.commands:
            return self.commands[command_name].execute(server, args)

        print("no command named", command_name)

    def __init__(self):
        self.commands = {}
        self.set_commands()
