import re

from re import Match

from plexapi.video import Movie

from jardim.stylish import stylish_p, Style

from stages.Stage import Stage
from stages.MovieStage import MovieStage
from Command import Command
from AppState import AppState
from config import ERROR_COLOR, MOVIE_SUBTITLE_LOOKBACK, REQUIRED_SUBTITLE_LANGS, SECONDARY_COLOR
from subtitles import display_missing_subtitles_2, get_missing_subtitle_langs_2, download_missing_subtitles
from utils import get_at_index_or_none, list_items, confirm

movieStage = MovieStage()


class MoviesStage(Stage):
    def __init__(self):
        super().__init__()
        self.commands = [
            Command(re.compile(r"list|all|movies"),
                    "Displays the list of movies",
                    _list_movies),
            Command(re.compile(r"\? (.+)"),
                    "Displays the list of movies that match the given input",
                    _list_movies),
            Command(re.compile(r"(\d+)"),
                    "Navigates to a specific movie",
                    _enter_movie_stage_by_idx),
            Command(re.compile(r"ms( -a)?( -d)?"),
                    "Displays/downloads missing subtitles",
                    _missing_subtitles),
            Command(re.compile(r"scan|update"),
                    "Scans the movies section for new media",
                    _scan_library_files)
        ]


def _list_movies(match: Match, state: AppState):
    movies = state.movies_section.all()

    query = get_at_index_or_none(match.groups(), 0)
    list_items([movie.title for movie in movies], query)


def _enter_movie_stage_by_idx(match: Match, state: AppState):
    movies = state.movies_section.all()

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

    filters = {}
    if not all_movies:
        filters["originallyAvailableAt>>"] = MOVIE_SUBTITLE_LOOKBACK

    movies: list[Movie] = state.movies_section.searchMovies(filters=filters)
    missing = get_missing_subtitle_langs_2(movies, REQUIRED_SUBTITLE_LANGS.keys())

    if download:
        download_missing_subtitles(missing)
    else:
        display_missing_subtitles_2(missing)


def _scan_library_files(_: Match, state: AppState):
    if confirm("You are about to scan the movies section"):
        stylish_p("Scaning movies section...", foreground=SECONDARY_COLOR, style=Style.LIGHT)
        state.movies_section.update()
