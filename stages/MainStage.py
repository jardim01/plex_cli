import re

from re import Match

from plexapi.library import ShowSection, MovieSection
from plexapi.server import PlexServer

from jardim_utils.stylish import stylish_p

from stages.Stage import Stage
from stages.ShowsStage import ShowsStage
from stages.MoviesStage import MoviesStage
from Command import Command
from AppState import AppState
from config import ERROR_COLOR
from exceptions import SectionNotFoundException

showsStage = ShowsStage()
moviesStage = MoviesStage()


class MainStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"tv|shows"), "Navigates to tv shows stage", _enter_shows_stage),
            Command(re.compile(r"movies"), "Navigates to movies stage", _enter_movies_stage)
        ]


def _get_shows_section(server: PlexServer) -> ShowSection:
    for s in server.library.sections():
        if isinstance(s, ShowSection):
            return s
    raise SectionNotFoundException()


def _enter_shows_stage(_: Match, state: AppState) -> None:
    try:
        section = _get_shows_section(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find tv show section", foreground=ERROR_COLOR)
        return

    showsStage.run_loop(state=state.copy(path=state.path + ["TV Shows"], shows_section=section))


def _get_movies_section(server: PlexServer) -> MovieSection:
    for s in server.library.sections():
        if isinstance(s, MovieSection):
            return s
    raise SectionNotFoundException()


def _enter_movies_stage(_: Match, state: AppState) -> None:
    try:
        section = _get_movies_section(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find movies section", foreground=ERROR_COLOR)
        return

    moviesStage.run_loop(state=state.copy(path=state.path + ["Movies"], movies_section=section))
