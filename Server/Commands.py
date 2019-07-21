class Command:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, args):
        raise ValueError("execute method not implemented")
