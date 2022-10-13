import re

from re import Match

from stages.MoviesStage import MoviesStage
from stages.Stage import Stage
from stages.ShowsStage import ShowsStage
from Command import Command
from AppState import AppState

showsStage = ShowsStage()
moviesStage = MoviesStage()


class MainStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"shows|tv"), "Navigates to shows stage", _enter_shows_stage),
            Command(re.compile(r"movies"), "Navigates to movies stage", _enter_movies_stage)
        ]


def _enter_shows_stage(_: Match, state: AppState) -> None:
    showsStage.run_loop(state=state.copy(path=state.path + ["TV Shows"]))


def _enter_movies_stage(_: Match, state: AppState) -> None:
    moviesStage.run_loop(state=state.copy(path=state.path + ["Movies"]))
