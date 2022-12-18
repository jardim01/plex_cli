import re

from re import Match

from jardim.stylish import stylish, stylish_p, Style

from Command import Command
from AppState import AppState
from config import GO_BACK, SECONDARY_COLOR, ERROR_COLOR
from utils import read_command


class Stage:
    def __init__(self):
        self.commands: list[Command] = []

    def _all_commands(self) -> list[Command]:
        return [
            Command(re.compile(r'help'), 'Displays this message', self._help_handler),
            *self.commands
        ]

    @staticmethod
    def _invalid_command_handler(cmd: str) -> None:
        stylish_p(f"Invalid command '{cmd}'", foreground=ERROR_COLOR)

    def _help_handler(self, _: Match, __: AppState) -> None:
        pattern_style = Style.BOLD
        for c in self._all_commands():
            s = stylish(c.pattern.pattern, foreground=SECONDARY_COLOR, style=pattern_style)
            s += f' - {c.description}'
            print(s)
        s = stylish(GO_BACK, foreground=SECONDARY_COLOR, style=pattern_style)
        s += f' - Navigates to previous stage'
        print(s)

    def run_loop(self, state: AppState) -> None:
        while True:
            cmd = read_command(state.path)
            if re.fullmatch(GO_BACK, cmd) is not None:
                break

            for c in self._all_commands():
                match = re.fullmatch(c.pattern, cmd)
                if match is None:
                    continue

                c.handler(match, state)
                break
            else:
                self._invalid_command_handler(cmd)
