import re

from re import Match

from plexapi.video import Episode

from jardim.stylish import stylish_p, stylish, Style

from stages.Stage import Stage
from stages.EpisodeStage import EpisodeStage
from Command import Command
from AppState import AppState
from config import SECONDARY_COLOR, SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS, ERROR_COLOR
from subtitles import get_missing_subtitle_langs_2, display_missing_subtitles_2, download_missing_subtitles
from utils import confirm, display_props, get_at_index_or_none, list_items

episodeStage = EpisodeStage()


class SeasonStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"list|all|episodes"),
                    "Displays the list of episodes",
                    _list_episodes),
            Command(re.compile(r"(\d+)"),
                    "Navigates to a specific episode",
                    _enter_episode_stage_by_idx),
            Command(re.compile(r"ms( -a)?( -d)?"),
                    "Displays/downloads missing subtitles",
                    _missing_subtitles),
            Command(re.compile(r"info|details"),
                    "Displays season info",
                    _display_info),
            Command(re.compile(r"refresh"),
                    "Refreshes season metadata",
                    _refresh_metadata),
        ]


def _list_episodes(match: Match, state: AppState):
    episodes = state.season.episodes()

    query = get_at_index_or_none(match.groups(), 0)
    list_items([episode.title for episode in episodes], query)


def _enter_episode_stage_by_idx(match: Match, state: AppState):
    episodes = state.season.episodes()

    idx = int(match.groups()[0]) - 1
    if idx in range(len(episodes)):
        episode = episodes[idx]
        _enter_episode_stage(episode, state)
    else:
        stylish_p("Invalid index", foreground=ERROR_COLOR)


def _enter_episode_stage(episode: Episode, state: AppState):
    episodeStage.run_loop(state.copy(path=state.path + [f"Episode {episode.episodeNumber}"], episode=episode))


def _missing_subtitles(match: Match, state: AppState):
    all_episodes = match.groups()[0] is not None
    download = match.groups()[1] is not None

    filters = {"season.id": state.season.ratingKey}
    if not all_episodes:
        filters["originallyAvailableAt>>"] = SUBTITLE_LOOKBACK

    episodes: list[Episode] = state.shows_section.searchEpisodes(filters=filters)
    missing = get_missing_subtitle_langs_2(episodes, REQUIRED_SUBTITLE_LANGS.keys())

    if download:
        download_missing_subtitles(missing)
    else:
        display_missing_subtitles_2(missing)


def _display_info(_: Match, state: AppState):
    display_props(state.season, lambda key, value: not key.startswith("_") and value is not None)


def _refresh_metadata(_: Match, state: AppState):
    msg = "You are about to refresh metadata for "
    msg += stylish(f"{state.season.parentTitle} - {state.season.title}", style=Style.BOLD)
    if confirm(msg):
        stylish_p("Refreshing metadata...", foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.season.refresh()
