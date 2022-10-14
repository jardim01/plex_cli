import re

from re import Match

from jardim_utils.stylish import Style, stylish, stylish_p

from stages.Stage import Stage
from Command import Command
from AppState import AppState
from config import REQUIRED_SUBTITLE_LANGS, SECONDARY_COLOR
from subtitles import get_missing_subtitle_langs, display_missing_subtitles, download_missing_subtitles
from utils import display_props, confirm


class EpisodeStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"ms( -d)?"),
                    "Displays/downloads missing subtitles",
                    _missing_subtitles),
            Command(re.compile(r"info|details"),
                    "Displays episode info",
                    _display_info),
            Command(re.compile(r"refresh"),
                    "Refreshes episode metadata",
                    _refresh_metadata),
        ]


def _missing_subtitles(match: Match, state: AppState):
    download = match.groups()[0] is not None

    missing = get_missing_subtitle_langs(state.episode, REQUIRED_SUBTITLE_LANGS.keys())
    if len(missing) == 0:
        return

    if download:
        download_missing_subtitles({state.episode: missing})
    else:
        display_missing_subtitles(state.episode, missing)


def _display_info(_: Match, state: AppState):
    display_props(state.episode, lambda key, value: not key.startswith("_") and value is not None)


def _refresh_metadata(_: Match, state: AppState):
    msg = "You are about to refresh metadata for "
    msg += stylish(f"{state.episode.grandparentTitle} {state.episode.seasonEpisode.upper()}", style=Style.BOLD)
    if confirm(msg):
        stylish_p("Refreshing metadata...", foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.episode.refresh()
