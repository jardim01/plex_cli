import humanize

from plexapi.video import Episode, Movie

from jardim_utils import opensubtitles
from jardim_utils.opensubtitles import OSLanguage, download_extract
from jardim_utils.stylish import stylish, Style, stylish_p, Color
from jardim_utils.utils import table, TableChars

from config import SECONDARY_COLOR, SUBTITLE_LANGS_FALLBACK, ERROR_COLOR, table_chars_transformation, \
    get_subtitle_download_path, SUCCESS_COLOR, WARNING_COLOR, after_subtitle_download, REQUIRED_SUBTITLE_LANGS
from exceptions import NoSubtitleResultsException
from utils import get_imdb_id, get_prompt


def download_missing_subtitles(missing: dict[Episode | Movie, list[str]]):
    idx = 0
    last_idx = sum([len(langs) for langs in missing.values()]) - 1
    downloaded = []
    for video, langs in missing.items():
        for lang in langs:
            os_lang: OSLanguage = REQUIRED_SUBTITLE_LANGS[lang]
            subtitle_path = download_subtitle_with_output(video, os_lang)
            if subtitle_path is not None:
                downloaded.append(subtitle_path)
            if idx != last_idx:
                print()
            idx += 1

    if len(downloaded) > 0:
        after_subtitle_download(*downloaded)


def get_missing_subtitle_langs_2(
        videos: list[Episode | Movie],
        required_langs: list[str]
) -> dict[Episode | Movie, list[str]]:
    missing = {}
    for video in videos:
        langs = get_missing_subtitle_langs(video, required_langs)
        if len(langs) > 0:
            missing[video] = langs
    return missing


def display_missing_subtitles_2(missing: dict[Episode | Movie, list[str]]):
    for video, langs in missing.items():
        display_missing_subtitles(video, langs)


def download_subtitle(video: Episode | Movie, lang: OSLanguage) -> str | None:
    if isinstance(video, Episode):
        imdb_id = get_imdb_id(video.show())
    else:
        imdb_id = get_imdb_id(video)

    if imdb_id is None:
        raise Exception("Failed to get imdb id")

    if isinstance(video, Episode):
        status, subtitles = opensubtitles.search(
            imdb_id=imdb_id,
            season=video.seasonNumber,
            episode=video.episodeNumber,
            language=lang
        )
    else:
        status, subtitles = opensubtitles.search(
            imdb_id=imdb_id,
            language=lang
        )

    if status not in range(200, 300):
        raise Exception(f"Failed to search for subtitles ({status})")

    if len(subtitles) == 0:
        raise NoSubtitleResultsException()

    subtitle = select_subtitle(subtitles)
    if subtitle is None:
        return None

    video_path = video.media[0].parts[0].file
    subtitle_path = get_subtitle_download_path(video_path, subtitle["ISO639"], subtitle["SubFormat"])

    download_extract(subtitle["SubDownloadLink"], subtitle_path)

    return subtitle_path


def select_subtitle(subtitles: list):
    headers = ["#", "File Name", "Format", "Episode", "HI", "AI", "Language", "Rating", "Downloads"]
    yes = stylish("✓", foreground=Color.GREEN)
    no = stylish("✗", foreground=Color.RED)
    values = []
    i = 1
    for sub in subtitles:
        values.append([
            stylish(str(i), foreground=SECONDARY_COLOR),
            sub["SubFileName"],
            sub["InfoFormat"],
            "" if sub['MovieKind'] == "movie" else f"S{int(sub['SeriesSeason']):02}E{int(sub['SeriesEpisode']):02}",
            yes if sub["SubHearingImpaired"] == "1" else no,
            yes if sub["SubAutoTranslation"] == "1" else no,
            sub["LanguageName"],
            sub["SubRating"],
            sub["SubDownloadsCnt"],
        ])
        i += 1
    print(table(
        values=values,
        headers=[stylish(h, foreground=SECONDARY_COLOR) for h in headers],
        table_chars=TableChars.default().transformed(table_chars_transformation))
    )

    user_input = input(get_prompt(["Choose subtitle"]))
    if user_input.isdigit():
        idx = int(user_input) - 1
        return subtitles[idx]

    return None


def display_missing_subtitles(video: Episode | Movie, langs: list[str]):
    if isinstance(video, Episode):
        tmp = f"{video.grandparentTitle} {video.seasonEpisode.upper()}"
    else:
        tmp = f"{video.title}"
    s = stylish(tmp,
                foreground=SECONDARY_COLOR,
                style=Style.BOLD)
    s += stylish(f" (aired {humanize.naturaltime(video.originallyAvailableAt)})",
                 foreground=SECONDARY_COLOR,
                 style=Style.LIGHT)
    s += stylish("> ",
                 foreground=SECONDARY_COLOR,
                 style=Style.BOLD)
    s += ", ".join(langs)
    print(s)


def get_missing_subtitle_langs(video: Episode | Movie, required_langs: list[str]) -> list[str]:
    video.reload(checkFiles=False)
    present_langs = [s.languageCode for s in video.subtitleStreams()]
    return [lang for lang in required_langs if lang not in present_langs]


def get_searching_string(video: Episode | Movie, os_lang: OSLanguage):
    s = stylish(
        f"Searching for subtitles for ",
        foreground=SECONDARY_COLOR,
        style=Style.LIGHT
    )
    if isinstance(video, Episode):
        tmp = f"{video.grandparentTitle} {video.seasonEpisode.upper()}"
    else:
        tmp = f"{video.title}"
    s += stylish(
        tmp,
        foreground=SECONDARY_COLOR,
        style=Style.BOLD
    )
    s += stylish(
        f" ({os_lang.value}) (aired {humanize.naturaltime(video.originallyAvailableAt)})",
        foreground=SECONDARY_COLOR,
        style=Style.LIGHT
    )
    return s


def download_subtitle_with_output(video: Episode | Movie, os_lang: OSLanguage):
    try:
        s = get_searching_string(video, os_lang)
        print(s)
        subtitle_path = download_subtitle(video, os_lang)
        if subtitle_path is not None:
            stylish_p(f"Subtitle downloaded to {subtitle_path}", foreground=SUCCESS_COLOR)

        return subtitle_path
    except NoSubtitleResultsException:
        fallback = SUBTITLE_LANGS_FALLBACK.get(os_lang)
        if fallback is None:
            stylish_p(f"No subtitles found ({os_lang.value})", foreground=WARNING_COLOR)
        else:
            stylish_p(f"No subtitles found ({os_lang.value}), using fallback ({fallback.value})",
                      foreground=WARNING_COLOR)
            return download_subtitle_with_output(video, fallback)
    except Exception as e:
        stylish_p(str(e), foreground=ERROR_COLOR)

    return None
