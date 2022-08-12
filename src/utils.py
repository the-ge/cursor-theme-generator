#!/usr/bin/env python3


from sys import _getframe, stderr
from os import path
from datetime import datetime
from logger import Logger


log = Logger().get_logger(__name__)


class Color:
    Dim = '\033[2;Nm'
    Rev = '\033[7;Nm'
    End = '\033[0m'

    def __init__(self):
        styles = {
            'Normal': 0,
            'Bold': 1,
            'Light': 2,
            'Italic': 3,
            'Underlined': 4,
            'Blink': 5,
        }
        fores = {
            'Black': 30,
            'Red': 31,
            'Green': 32,
            'Yellow': 33,
            'Blue': 34,
            'Purple': 35,
            'Cyan': 36,
            'White': 37,
        }
        backs = {
            'Black': 40,
            'Red': 41,
            'Green': 42,
            'Yellow': 43,
            'Blue': 44,
            'Purple': 45,
            'Cyan': 46,
            'White': 47,
        }
        dark = (
            'Black',
            'Red',
            'Blue',
            'Purple',
        )

        for f, fore in fores.items():
            for s, style in styles.items():
                kf = f
                ks = s
                if s == 'Normal':
                    ks = ''
                setattr(self, f'{kf}{ks}', self.ansi(f'{style};{fore}'))
        for b, back in backs.items():
            for s, style in styles.items():
                (kf, fore) = ('Black', fores['Black'])
                kb = ''
                ks = s
                if b:
                    kb = f'On{b}'
                    if b in dark:
                        (kf, fore) = ('White', fores['White'])
                if s == 'Normal':
                    ks = ''
                setattr(self, f'{ks}{kb}', self.ansi(f'{style};{fore};{back}'))

    def ansi(self, code):
        return f'\033[{code}m'

    def test(self):
        for c, code in self.__dict__.items():
            print(f'{c.ljust(18)}: {code}Testing!{self.End}')


def D(*args):
    file = path.basename(_getframe(1).f_code.co_filename)
    line = str(_getframe(1).f_lineno)
    prefix = f'{Color.Yellow}'
    separator = f'{Color.End} {Color.OnCyan}'
    stderr_print(args, file, line, separator, prefix)


def E(*args):
    file = path.basename(_getframe(1).f_code.co_filename)
    line = str(_getframe(1).f_lineno)
    stderr_print(args, file, line, '▊', f'{Color.WhiteLight}')


def report(msg):
    print(f'{Color.Yellow}[{now()}]{Color.Cyan} {msg} {Color.End}')


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters#answer-34325723
def print_progress(iteration, total, length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        length      - Optional  : character length of bar (int)
    """
    if not Logger().debug_enabled():
        filled = length * iteration // total  # // is the Python floor division operator
        bar = '⯀' * filled + '-' * (length - filled)
        print(f'\r{Color.WhiteLight}{bar}{Color.End}{iteration: {len(str(total))}d}/{total}', end='\r')
        if iteration == total:  # print New Line on Complete
            print()


def print_sep(length=72):
    print('‐' * length)


def stderr_print(args, file, line, separator='|', prefix=''):
    # prefix: ' ❶ '
    # separator: ' ❷ '
    # print(f'{prefix}[{time}] {file}:{line} {separator}', end='❸')
    # for arg in args:
    #     print(arg, end=separator)
    # print('❹')
    # prints --> ❶ [13:16:13.511978] main.py:36  ❷ ❸Variable #1 ❷ Variable #2 ❷ Variable #3 ❷ ❹
    stderr.write(f'{prefix}[{now()}] {file}:{line}{separator}')
    for arg in args:
        stderr.write(f'{arg}{separator}')
    stderr.write(Color.End + '\n')


def now():
    return datetime.now().strftime('%H:%M:%S.%f')


Color = Color()
# Color.test()
