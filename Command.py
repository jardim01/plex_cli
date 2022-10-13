from re import Pattern, Match
from typing import Callable

from AppState import AppState


class Command:
    def __init__(self, pattern: Pattern, description: str, handler: Callable[[Match, AppState], None]):
        self.pattern = pattern
        self.description = description
        self.handler = handler
