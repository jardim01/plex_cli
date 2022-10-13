import re

from plexapi.library import Guid
from plexapi.video import Show, Movie

from jardim_utils.stylish import stylish, Style

from config import PRIMARY_COLOR, SECONDARY_COLOR


def get_prompt(path: list[str]) -> str:
    separator = stylish("\\", style=Style.LIGHT)
    parts = [stylish(f, foreground=PRIMARY_COLOR, style=Style.BOLD) for f in path]
    return separator.join(parts) + stylish(">", style=Style.LIGHT) + " "


def read_command(path: list[str]) -> str:
    prompt = get_prompt(path)
    return input(prompt)


def get_at_index_or_none(items, idx: int):
    if idx in range(len(items)):
        return items[idx]
    return None


def get_imdb_id(item: Show | Movie):
    pattern = re.compile(r"imdb://tt(\d{7,})")
    guid: Guid
    for guid in item.guids:
        match = pattern.match(guid.id)
        if match is not None:
            return int(match.groups()[0])

    return None


def list_items(items: list[str], query: str):
    idx = 1
    for item in items:
        if query is None or query.lower() in item.lower():
            s = stylish(f"{idx}. ", foreground=SECONDARY_COLOR)
            s += item
            print(s)
        idx += 1
