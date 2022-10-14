import copy

from plexapi.library import ShowSection, MovieSection
from plexapi.server import PlexServer
from plexapi.video import Show, Movie, Season, Episode


class AppState:
    def __init__(
            self,
            path: list[str],
            server: PlexServer,
            shows_section: ShowSection = None,
            show: Show = None,
            season: Season = None,
            episode: Episode = None,
            movies_section: MovieSection = None,
            movie: Movie = None
    ):
        self.path = path
        self.server = server
        self.shows_section = shows_section
        self.show = show
        self.season = season
        self.episode = episode
        self.movies_section = movies_section
        self.movie = movie

    def copy(
            self,
            path: list[str] = None,
            server: PlexServer = None,
            shows_section: ShowSection = None,
            show: Show = None,
            season: Season = None,
            episode: Episode = None,
            movies_section: MovieSection = None,
            movie: Movie = None
    ):
        new_state = copy.deepcopy(self)
        if path is not None:
            new_state.path = path
        if server is not None:
            new_state.server = server
        if shows_section is not None:
            new_state.shows_section = shows_section
        if show is not None:
            new_state.show = show
        if season is not None:
            new_state.season = season
        if episode is not None:
            new_state.episode = episode
        if movies_section is not None:
            new_state.movies_section = movies_section
        if movie is not None:
            new_state.movie = movie
        return new_state
