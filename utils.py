import re
from typing import Any, Callable

from plexapi.library import Guid
from plexapi.video import Show, Movie

from jardim.stylish import stylish, Style

from config import PRIMARY_COLOR, SECONDARY_COLOR, PROMPT_COLOR, PROMPT_SYMBOL, SEPARATOR_SYMBOL, INPUT_COLOR, \
    INPUT_STYLE


def stylish_input(prompt) -> str:
    try:
        print(prompt, end=stylish('', foreground=INPUT_COLOR, style=INPUT_STYLE, endc=False))
        user_input = input()
        print(end=stylish(''))
        return user_input
    except BaseException as e:
        print(stylish(''))
        raise e


def get_prompt(msg: str) -> str:
    prompt = stylish(msg, foreground=PROMPT_COLOR, style=Style.BOLD)
    prompt += PROMPT_SYMBOL + ' '
    return prompt


def read_command(path: list[str]) -> str:
    parts = [stylish(f, foreground=PRIMARY_COLOR, style=Style.BOLD) for f in path]
    text = SEPARATOR_SYMBOL.join(parts) + PROMPT_SYMBOL + ' '
    return stylish_input(text)


def get_at_index_or_none(items, idx: int):
    if idx in range(len(items)):
        return items[idx]
    return None


def get_imdb_id(item: Show | Movie):
    pattern = re.compile(r'imdb://tt(\d{7,})')
    guid: Guid
    for guid in item.guids:
        match = pattern.match(guid.id)
        if match is not None:
            return int(match.groups()[0])

    return None


def list_items(items: list[str], query: str | None):
    idx = 1
    for item in items:
        if query is None or query.lower() in item.lower():
            s = stylish(f'{idx}. ', foreground=SECONDARY_COLOR, style=Style.BOLD)
            s += item
            print(s)
        idx += 1


def display_props(obj: Any, filter_props: Callable[[str, Any], bool] = lambda _, __: True):
    for key, value in vars(obj).items():
        if filter_props(key, value):
            s = stylish(key, foreground=SECONDARY_COLOR, style=Style.BOLD)
            s += stylish(': ', foreground=SECONDARY_COLOR, style=Style.LIGHT)
            s += str(value)
            print(s)


def confirm(msg: str):
    print(msg)
    prompt = stylish('Are you sure you want to proceed?', foreground=PROMPT_COLOR)
    prompt += stylish(' (y/n)', foreground=PROMPT_COLOR, style=Style.LIGHT)
    prompt += PROMPT_SYMBOL + ' '
    user_input = stylish_input(prompt).strip()
    if user_input == 'y':
        return True
    else:
        return False
