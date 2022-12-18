import re

from re import Match

from plexapi.video import Show, Episode

from jardim.stylish import stylish_p, Style

from stages.Stage import Stage
from stages.ShowStage import ShowStage
from Command import Command
from AppState import AppState
from config import EPISODE_THUMBNAIL_LOOKBACK, ERROR_COLOR, EPISODE_SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS, \
    SECONDARY_COLOR
from subtitles import get_missing_subtitle_langs_2, display_missing_subtitles_2, download_missing_subtitles
from utils import get_at_index_or_none, list_items, confirm
from video_preview_thumbnails import display_missing_video_preview_thumbnails

showStage = ShowStage()


class ShowsStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r'list|all|shows'),
                    'Displays the list of tv shows',
                    _list_shows),
            Command(re.compile(r'\? (.+)'),
                    'Displays the list of tv shows that match the given input',
                    _list_shows),
            Command(re.compile(r'(\d+)'),
                    'Navigates to a specific tv show',
                    _enter_show_stage_by_idx),
            Command(re.compile(r'ms( -a)?( -d)?'),
                    'Displays/downloads missing subtitles',
                    _missing_subtitles),
            Command(re.compile(r'mvpt( -a)?( -g)?'),
                    'Displays/generates missing video preview thumbnails',
                    _missing_video_preview_thumbnails),
            Command(re.compile(r'scan|update'),
                    'Scans the tv shows section for new media',
                    _scan_library_files)
        ]


def _list_shows(match: Match, state: AppState):
    shows = state.shows_section.all()

    query = get_at_index_or_none(match.groups(), 0)
    list_items([show.title for show in shows], query)


def _enter_show_stage_by_idx(match: Match, state: AppState):
    shows = state.shows_section.all()

    idx = int(match.groups()[0]) - 1
    if idx in range(len(shows)):
        show = shows[idx]
        _enter_show_stage(show, state)
    else:
        stylish_p('Invalid index', foreground=ERROR_COLOR)


def _enter_show_stage(show: Show, state: AppState):
    showStage.run_loop(state.copy(path=state.path + [show.title], show=show))


def _missing_subtitles(match: Match, state: AppState):
    all_episodes = match.groups()[0] is not None
    download = match.groups()[1] is not None

    filters = {}
    if not all_episodes:
        filters['originallyAvailableAt>>'] = EPISODE_SUBTITLE_LOOKBACK

    episodes: list[Episode] = state.shows_section.searchEpisodes(filters=filters)
    missing = get_missing_subtitle_langs_2(episodes, REQUIRED_SUBTITLE_LANGS.keys())

    if download:
        download_missing_subtitles(missing)
    else:
        display_missing_subtitles_2(missing)


def _missing_video_preview_thumbnails(match: Match, state: AppState):
    all_episodes = match.groups()[0] is not None
    generate = match.groups()[1] is not None

    filters = {}
    if not all_episodes:
        filters['originallyAvailableAt>>'] = EPISODE_THUMBNAIL_LOOKBACK

    episodes: list[Episode] = state.shows_section.searchEpisodes(filters=filters)
    missing = [e for e in episodes if not e.hasPreviewThumbnails]

    for e in missing:
        display_missing_video_preview_thumbnails(e)
        if generate:
            e.analyze()


def _scan_library_files(_: Match, state: AppState):
    if confirm('You are about to scan the tv shows section'):
        stylish_p('Scaning tv shows section...', foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.shows_section.update()
