import time #Uptime
import json #Load_Aliases
import os   #Load_Aliases
import hashlib #Load_Map


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

class List(Command):
    def __init__(self):
        NAME="list"
        DESCRIPTION="Print the number of connected player"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        message = "{} players connected".format(server.online_player)
        server.drawer.addstr(message)

class Uptime(Command):
    def __init__(self):
        NAME="uptime"
        DESCRIPTION="Print for how long the server has been running"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        now = time.time()
        elapse_time = now - server.start_time
        time_format = time.strftime("%M:%S", time.gmtime(elapse_time))
        server.drawer.addstr("{}".format(time_format))

class Clear(Command):
    def __init__(self):
        NAME="clear"
        DESCRIPTION="Clear the server screen"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        server.drawer.clear_screen()

class List_Aliases(Command):
    def __init__(self):
        NAME="list_aliases"
        DESCRIPTION="Print all loaded aliases"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        server.drawer.addstr("Loaded aliases :")
        for alias in server.aliases:
            alias_name, alias_args = server.get_alias(alias)
            msg = "    - {} : {} {}".format(alias, alias_name, *alias_args)
            server.drawer.addstr(msg)

class Set_Alias(Command):
    def __init__(self):
        NAME="set_alias"
        DESCRIPTION="Save an alias"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if len(args) < 2:
            print("You need to provide at least the alias name and the command name")
            return 0

        name = args[0] #Alias name
        alias = args[1] #Actual command
        alias_args = args[2:] if len(args) > 1 else ""
        server.aliases[name] = alias + " " + " ".join(alias_args)
        server.save_aliases()

class Load_Aliases(Command):
    def __init__(self):
        NAME="load_aliases"
        DESCRIPTION="Load aliases in 'aliases.json'"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if os.path.exists(server.aliases_file_path):
            with open(server.aliases_file_path, 'r') as f:
                json_data = f.read()
                data = json.loads(json_data)
                server.aliases = data
            server.drawer.addstr("Aliases file loaded")
        else:
            server.drawer.addstr("No aliases file")

class Print_Alias(Command):
    def __init__(self):
        NAME="print_alias"
        DESCRIPTION="Print the command associated with the alias"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if not args:
            server.drawer.addstr("No alias was given")
            return 0

        alias = server.get_alias(args[0])
        alias_name = alias[0]
        alias_args = " ".join(str(x[0]) for x in alias[1:])
        if alias:
            server.drawer.addstr("{} -> {}".format(alias_name, alias_args))

class Clear_Playlist(Command):
    def __init__(self):
        NAME="clear_playlist"
        DESCRIPTION="Remove all maps in the current loaded playlist"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        server.map_playlist.clear()
        server.drawer.addstr("Playlist cleared")

class Load_Playlist(Command):
    def __init__(self):
        NAME="load_playlist"
        DESCRIPTION="Load a map playlist from a file"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if not args:
            server.drawer.addstr("No file path provided")
            return

        file_path = " ".join(args)
        if os.path.exists(file_path):
            with open(file_path) as f:
                for line in f.read().splitlines():
                    server.add_map([line])
        else:
            server.drawer.addstr("The given file does not exists")

class Add_Map(Command):
    def __init__(self):
        NAME="add_map"
        DESCRIPTION="Load a map into the playlist"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if not args:
            server.drawer.addstr("No map name provided")
            return
        map_name = args[0]
        map_path = os.path.join(server.map_folder, map_name)
        if os.path.exists(map_path):
            server.map_playlist.append(map_name)
            server.drawer.addstr("Map added to the playlist")
        else:
            server.drawer.addstr("There is no map named '{}'".format(map_name))

class Load_Map(Command):
    def __init__(self):
        NAME="load_map"
        DESCRIPTION="Load the a map from a file"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if server.online_player != 2:
            server.drawer.addstr("You need to be 2 players in order to play and load a map")
            return

        map_name = args[0]
        map_path = os.path.join(server.map_folder, map_name)
        server.drawer.addstr(map_path)
        if os.path.exists(map_path):
            map_hash = self.hash_map(map_path)
            server.drawer.addstr("Map hash: {}".format(map_hash))
            server.send_message_to_all_client("map_hash {} {}".format(map_name, map_hash))
            server.loaded_map_name.clear()
            server.loaded_map_name.append(map_name)
        else:
            server.drawer.addstr("The map {} does not exist".format(map_name))
            server.loaded_map_path = None

    def hash_map(self, map_path):
        with open(map_path, 'r') as f:
            map_hash = hashlib.sha256(f.read().encode()).hexdigest()
            return map_hash

class Next_Map(Command):
    def __init__(self):
        NAME="next_map"
        DESCRIPTION="Load the next map"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if server.map_playlist:
            next_map = server.map_playlist.pop(0)
            server.load_map([next_map])
        else: #If there is no more map in the playlist, just reload the current loaded one
            server.command_map.execute(server, "reload_map", "")

class Reload_Map(Command):
    def __init__(self):
        NAME="reload_map"
        DESCRIPTION="Reload the currently loaded map"
        Command.__init__(self,NAME,DESCRIPTION)

    def execute(self, server, args):
        if server.loaded_map_name:
            server.command_map.execute(server, "load_map", server.loaded_map_name)
        else:
            server.drawer.addstr("No map is currently loaded")
