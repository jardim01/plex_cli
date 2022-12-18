import re

from re import Match

from jardim.stylish import stylish, Style, stylish_p

from stages.Stage import Stage
from Command import Command
from AppState import AppState
from config import REQUIRED_SUBTITLE_LANGS, SECONDARY_COLOR
from subtitles import get_missing_subtitle_langs, download_missing_subtitles, display_missing_subtitles
from utils import display_props, confirm


class MovieStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r'ms( -d)?'),
                    'Displays/downloads missing subtitles',
                    _missing_subtitles),
            Command(re.compile(r'info|details'),
                    'Displays movie info',
                    _display_info),
            Command(re.compile(r'refresh'),
                    'Refreshes movie metadata',
                    _refresh_metadata),
        ]


def _missing_subtitles(match: Match, state: AppState):
    download = match.groups()[0] is not None

    missing = get_missing_subtitle_langs(state.movie, REQUIRED_SUBTITLE_LANGS.keys())
    if len(missing) == 0:
        return

    if download:
        download_missing_subtitles({state.movie: missing})
    else:
        display_missing_subtitles(state.movie, missing)


def _display_info(_: Match, state: AppState):
    display_props(state.movie, lambda key, value: not key.startswith('_') and value is not None)


def _refresh_metadata(_: Match, state: AppState):
    msg = 'You are about to refresh metadata for '
    msg += stylish(f'{state.movie.title}', style=Style.BOLD)
    if confirm(msg):
        stylish_p('Refreshing metadata...', foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.episode.refresh()
