import re

from re import Match

from plexapi.library import ShowSection
from plexapi.server import PlexServer
from plexapi.video import Show, Episode

from jardim_utils.stylish import stylish_p

from AppState import AppState
from Command import Command
from config import ERROR_COLOR, SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS
from exceptions import SectionNotFoundException
from stages.ShowStage import ShowStage
from stages.Stage import Stage
from subtitles import get_missing_subtitle_langs_2, download_missing_subtitles, display_missing_subtitles_2
from utils import get_at_index_or_none, list_items

showStage = ShowStage()


class ShowsStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"list|all|shows"),
                    "Displays the list of TV Shows",
                    _list_shows),
            Command(re.compile(r"\? (.+)"),
                    "Displays the list of TV Shows that match the given input",
                    _list_shows),
            Command(re.compile(r"(\d+)"),
                    "Navigates to a specific show",
                    _enter_show_stage_by_idx),
            Command(re.compile(r"ms( -a)?( -d)?"),
                    "Displays/downloads missing subtitles",
                    _missing_subtitles)
        ]


def _get_shows_section(server: PlexServer) -> ShowSection:
    for s in server.library.sections():
        if isinstance(s, ShowSection):
            return s
    raise SectionNotFoundException()


def _get_shows(server: PlexServer) -> list[Show]:
    return _get_shows_section(server).all()


def _list_shows(match: Match, state: AppState):
    try:
        shows: list[Show] = _get_shows(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find TV Show section", foreground=ERROR_COLOR)
        return

    query = get_at_index_or_none(match.groups(), 0)
    list_items([show.title for show in shows], query)


def _enter_show_stage_by_idx(match: Match, state: AppState):
    try:
        shows = _get_shows(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find TV Show section", foreground=ERROR_COLOR)
        return

    idx = int(match.groups()[0]) - 1
    if idx in range(len(shows)):
        show = shows[idx]
        _enter_show_stage(show, state)
    else:
        stylish_p("Invalid index", foreground=ERROR_COLOR)


def _enter_show_stage(show: Show, state: AppState):
    showStage.run_loop(state.copy(path=state.path + [show.title], show=show))


def _missing_subtitles(match: Match, state: AppState):
    all_episodes = match.groups()[0] is not None
    download = match.groups()[1] is not None

    try:
        section = _get_shows_section(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find TV Show section", foreground=ERROR_COLOR)
        return

    filters = {}
    if not all_episodes:
        filters["originallyAvailableAt>>"] = SUBTITLE_LOOKBACK

    episodes: list[Episode] = section.searchEpisodes(filters=filters)
    missing = get_missing_subtitle_langs_2(episodes, REQUIRED_SUBTITLE_LANGS.keys())

    if download:
        download_missing_subtitles(missing)
        pass
    else:
        display_missing_subtitles_2(missing)
