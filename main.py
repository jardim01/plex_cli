from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

from jardim_utils.stylish import stylish_p

from stages.MainStage import MainStage
from AppState import AppState
from config import PLEX_TOKEN, PLEX_SERVER_NAME, ERROR_COLOR


def main():
    try:
        account: MyPlexAccount = MyPlexAccount(token=PLEX_TOKEN)
        server: PlexServer = account.resource(name=PLEX_SERVER_NAME).connect(ssl=True, locations=['remote'])
        state = AppState(path=[server.friendlyName], server=server)
        MainStage().run_loop(state)
    except Exception as e:
        stylish_p(str(e), foreground=ERROR_COLOR)
        exit(1)


if __name__ == '__main__':
    main()
