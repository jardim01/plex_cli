import humanize
from jardim.stylish import Style, stylish
from plexapi.video import Episode, Movie

from config import SECONDARY_COLOR


def display_missing_video_preview_thumbnails(video: Episode | Movie):
    if isinstance(video, Episode):
        tmp = f'{video.grandparentTitle} {video.seasonEpisode.upper()}'
    else:
        tmp = f'{video.title}'
    s = stylish(tmp,
                foreground=SECONDARY_COLOR,
                style=Style.BOLD)
    s += stylish(f' (aired {humanize.naturaltime(video.originallyAvailableAt)})',
                 foreground=SECONDARY_COLOR,
                 style=Style.LIGHT)
    print(s)
