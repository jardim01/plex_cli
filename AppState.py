import copy

from plexapi.server import PlexServer
from plexapi.video import Show, Movie


class AppState:
    def __init__(self, path: list[str], server: PlexServer, show: Show = None, movie: Movie = None):
        self.path = path
        self.server = server
        self.show = show
        self.movie = movie

    def copy(self, path: list[str] = None, server: PlexServer = None, show: Show = None, movie: Movie = None):
        new_state = copy.deepcopy(self)
        if path is not None:
            new_state.path = path
        if server is not None:
            new_state.server = server
        if show is not None:
            new_state.show = show
        if movie is not None:
            new_state.movie = movie
        return new_state
