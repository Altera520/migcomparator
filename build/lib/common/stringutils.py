import re
from typing import Any

CR = 0x0D
LF = 0x0A
EMPTY = ''
SPACE = ' '
ASTERISK = '*'
ESCAPE = '`'


def strip_margin(text: str) -> str:
    return re.sub('\n[ \t]*\|', '\n', text)


def strip_heredoc(text: str) -> str:
    indent = len(min(re.findall('\n[ \t]*(?=\S)', text) or ['']))
    pattern = r'\n[ \t]{%d}' % (indent - 1)
    return re.sub(pattern, '\n', text)


def lpad(value: Any, width: int, fillchar=SPACE) -> str:
    return str(value).rjust(width, fillchar)


def rpad(value: Any, width: int, fillchar=SPACE) -> str:
    return str(value).ljust(width, fillchar)


def escape(text: str) -> str:
    """
    백틱으로 escpae 처리
    :param text:
    :return:
    """
    if text.strip() == '*':
        return text
    return f'{ESCAPE}{text}{ESCAPE}' if str != ASTERISK else ASTERISK
