from Bot_Manager.welcome_text import welcome_text


class CommandLineTool:
    available_commands = ["general", "server", "account", "game", "proxy"]

    def __init__(self):
        self.mode = "general"

    def command_line_loop(self):
        print(welcome_text)
        command = input(f"COMMAND ({self.mode}) >>").strip().lower()
        print(command)
