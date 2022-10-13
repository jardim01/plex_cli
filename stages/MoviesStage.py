import re

from re import Match

from plexapi.library import MovieSection
from plexapi.server import PlexServer
from plexapi.video import Movie

from jardim_utils.stylish import stylish_p

from AppState import AppState
from Command import Command
from config import ERROR_COLOR, SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS
from exceptions import SectionNotFoundException
from stages.MovieStage import MovieStage
from stages.Stage import Stage
from utils import get_at_index_or_none, list_items
from subtitles import display_missing_subtitles_2, download_missing_subtitles, \
    get_missing_subtitle_langs_2

movieStage = MovieStage()


class MoviesStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"list|all|movies"),
                    "Displays the list of Movies",
                    _list_movies),
            Command(re.compile(r"\? (.+)"),
                    "Displays the list of Movies that match the given input",
                    _list_movies),
            Command(re.compile(r"(\d+)"),
                    "Navigates to a specific movie",
                    _enter_movie_stage_by_idx),
            Command(re.compile(r"ms( -a)?( -d)?"),
                    "Displays/downloads missing subtitles",
                    _missing_subtitles)
        ]


def _get_movies_section(server: PlexServer) -> MovieSection:
    for s in server.library.sections():
        if isinstance(s, MovieSection):
            return s
    raise SectionNotFoundException()


def _get_movies(server: PlexServer) -> list[Movie]:
    return _get_movies_section(server).all()


def _list_movies(match: Match, state: AppState):
    try:
        movies: list[Movie] = _get_movies(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find Movies section", foreground=ERROR_COLOR)
        return

    query = get_at_index_or_none(match.groups(), 0)
    list_items([movie.title for movie in movies], query)


def _enter_movie_stage_by_idx(match: Match, state: AppState):
    try:
        movies = _get_movies(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find Movies section", foreground=ERROR_COLOR)
        return

    idx = int(match.groups()[0]) - 1
    if idx in range(len(movies)):
        movie = movies[idx]
        _enter_movie_stage(movie, state)
    else:
        stylish_p("Invalid index", foreground=ERROR_COLOR)


def _enter_movie_stage(movie: Movie, state: AppState):
    movieStage.run_loop(state.copy(path=state.path + [movie.title], movie=movie))


def _missing_subtitles(match: Match, state: AppState):
    all_movies = match.groups()[0] is not None
    download = match.groups()[1] is not None

    try:
        section = _get_movies_section(state.server)
    except SectionNotFoundException:
        stylish_p("Failed to find Movies section", foreground=ERROR_COLOR)
        return

    filters = {}
    if not all_movies:
        filters["originallyAvailableAt>>"] = SUBTITLE_LOOKBACK

    movies: list[Movie] = section.searchMovies(filters=filters)
    missing = get_missing_subtitle_langs_2(movies, REQUIRED_SUBTITLE_LANGS.keys())

    if download:
        download_missing_subtitles(missing)
    else:
        display_missing_subtitles_2(missing)
