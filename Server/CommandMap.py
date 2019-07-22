from Commands import *

class CommandMap:
    def set_commands(self):
        #Utils
        self.register("exit", Exit())
        self.register("quit", Exit())
        self.register("list", List())
        self.register("uptime", Uptime())
        self.register("clear", Clear())

        #Aliases
        self.register("list_aliases", List_Aliases())
        self.register("set_alias", Set_Alias())
        self.register("load_aliases", Load_Aliases())
        self.register("print_alias", Print_Alias())

        #Map
        self.register("clear_playlist", Clear_Playlist())
        self.register("load_playlist", Load_Playlist())
        self.register("add_map", Add_Map())
        self.register("load_map", Load_Map())
        self.register("next_map", Next_Map())
        self.register("reload_map", Reload_Map())

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
