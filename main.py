import sys

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.exceptions import BadRequest

from jardim.stylish import stylish_p

from stages.MainStage import MainStage
from AppState import AppState
from config import PLEX_TOKEN, PLEX_SERVER_NAME, ERROR_COLOR

EXIT_FAILURE = 1


def main():
    try:
        account: MyPlexAccount = MyPlexAccount(token=PLEX_TOKEN)
        server: PlexServer = account.resource(name=PLEX_SERVER_NAME).connect(ssl=True, locations=['remote'])
    except Exception as e:
        msg = 'Failed to login to Plex' if isinstance(e, BadRequest) else str(e)
        stylish_p(msg, foreground=ERROR_COLOR)
        sys.exit(EXIT_FAILURE)

    try:
        state = AppState(path=[server.friendlyName], server=server)
        MainStage().run_loop(state)
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
