import os

from jardim.subtitles.OSLanguage import OSLanguage
from jardim.stylish import Color, stylish, Style

from plugins import convert_to_utf8, open_subtitle_cleaner

PLEX_TOKEN = os.environ['PLEX_TOKEN']
PLEX_SERVER_NAME = os.environ['PLEX_SERVER_NAME']

PRIMARY_COLOR = 197  # Magenta
SECONDARY_COLOR = 49  # Aqua
ERROR_COLOR = Color.RED
WARNING_COLOR = Color.YELLOW
SUCCESS_COLOR = Color.GREEN
PROMPT_COLOR = Color.CYAN
INPUT_COLOR = Color.GREY
INPUT_STYLE = Style.ITALICIZED

PROMPT_SYMBOL = '>'
SEPARATOR_SYMBOL = '\\'

GO_BACK = '\\.\\.'

EPISODE_SUBTITLE_LOOKBACK = '60d'
EPISODE_THUMBNAIL_LOOKBACK = '60d'
MOVIE_SUBTITLE_LOOKBACK = '180d'
MOVIE_THUMBNAIL_LOOKBACK = '180d'
REQUIRED_SUBTITLE_LANGS = {
    'eng': OSLanguage.ENGLISH,
    'por': OSLanguage.PORTUGUESE
}
SUBTITLE_LANGS_FALLBACK = {
    OSLanguage.PORTUGUESE: OSLanguage.PORTUGUESE_BR
}


def table_chars_transformation(s):
    return stylish(s, style=Style.LIGHT)


def get_subtitle_download_path(episode_path: str, iso639: str, fmt: str):
    sub_path = episode_path.replace('/media/andre/Hercules/', 'F:\\').replace('/', '\\')
    lang_repr = iso639
    if lang_repr == 'pb':
        lang_repr = 'pt-BR'
    name, _ = os.path.splitext(sub_path)
    return f'{name}.{lang_repr}.{fmt}'


def after_subtitle_download(*subtitle_paths: str):
    for p in subtitle_paths:
        convert_to_utf8(p)
    open_subtitle_cleaner(subtitle_paths)
