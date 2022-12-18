import re

from re import Match

from plexapi.video import Season, Episode

from jardim.stylish import stylish_p, stylish, Style

from stages.Stage import Stage
from stages.SeasonStage import SeasonStage
from Command import Command
from AppState import AppState
from config import EPISODE_THUMBNAIL_LOOKBACK, ERROR_COLOR, EPISODE_SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS, \
    SECONDARY_COLOR
from subtitles import get_missing_subtitle_langs_2, display_missing_subtitles_2, download_missing_subtitles
from utils import list_items, display_props, confirm
from video_preview_thumbnails import display_missing_video_preview_thumbnails

seasonStage = SeasonStage()


class ShowStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r'list|all|seasons'),
                    'Displays the list of seasons',
                    _list_seasons),
            Command(re.compile(r'(\d+)'),
                    'Navigates to a specific season',
                    _enter_season_stage_by_idx),
            Command(re.compile(r'ms( -a)?( -d)?'),
                    'Displays/downloads missing subtitles',
                    _missing_subtitles),
            Command(re.compile(r'mvpt( -a)?( -g)?'),
                    'Displays/generates missing video preview thumbnails',
                    _missing_video_preview_thumbnails),
            Command(re.compile(r'info|details'),
                    'Displays tv show info',
                    _display_info),
            Command(re.compile(r'refresh'),
                    'Refreshes tv show metadata',
                    _refresh_metadata),
        ]


def _list_seasons(_: Match, state: AppState):
    list_items([season.title for season in state.show.seasons()], None)


def _enter_season_stage_by_idx(match: Match, state: AppState):
    seasons = state.show.seasons()

    idx = int(match.groups()[0]) - 1
    if idx in range(len(seasons)):
        season = seasons[idx]
        _enter_season_stage(season, state)
    else:
        stylish_p('Invalid index', foreground=ERROR_COLOR)


def _enter_season_stage(season: Season, state: AppState):
    seasonStage.run_loop(state.copy(path=state.path + [season.title], season=season))


def _missing_subtitles(match: Match, state: AppState):
    all_episodes = match.groups()[0] is not None
    download = match.groups()[1] is not None

    filters = {'show.id': state.show.ratingKey}
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

    filters = {'show.id': state.show.ratingKey}
    if not all_episodes:
        filters['originallyAvailableAt>>'] = EPISODE_THUMBNAIL_LOOKBACK

    episodes: list[Episode] = state.shows_section.searchEpisodes(filters=filters)
    missing = [e for e in episodes if not e.hasPreviewThumbnails]

    for e in missing:
        display_missing_video_preview_thumbnails(e)
        if generate:
            e.analyze()


def _display_info(_: Match, state: AppState):
    display_props(state.show, lambda key, value: not key.startswith('_') and value is not None)


def _refresh_metadata(_: Match, state: AppState):
    msg = 'You are about to refresh metadata for '
    msg += stylish(state.show.title, style=Style.BOLD)
    if confirm(msg):
        stylish_p('Refreshing metadata...', foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.show.refresh()
