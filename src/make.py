#!/usr/bin/env python3
#
# This script combines hotspot files and PNGs to X11 cursor files.
# Copyright (C) 2018 Gerhard Großmann
# Converted to Python
# Copyright (C) 2018 2022 Gabriel Tenita


from os import makedirs, path as ospath, scandir, symlink
from argparse import ArgumentParser
from shutil import copyfile, make_archive, rmtree
from subprocess import DEVNULL, run
from re import sub
from datetime import datetime
from assets_generator import CursorThemeAssetsGenerator
from utils import report
from logger import Logger
import logging


default_sizes = '24'  # 24 32 48 64 96 128; 24 is required as the base for hotspots calculation
logging.root.setLevel(logging.ERROR)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
log = Logger().get_logger(__name__)


class Paths(object):
    source = './themes'
    build_root = './build'
    dist_root = './dist'
    export = './export'
    source_file = 'cursors.svg'
    hotspots_dir = 'hotspots'
    pngs_dir = 'pngs'
    cursors_dir = 'cursors'

    def __init__(self, theme_dir):
        self.build = f'{self.build_root}/{theme_dir}'
        self.dist = f'{self.dist_root}/{theme_dir}'
        self.export_source = f'{self.build}/{self.source_file}'

    def export_file(self, name, size, prefix=''):
        return f'{self.build}/{self.pngs_dir}/{size}/{prefix}{name}.png'

    def hotspots_file(self, cursor_name):
        return f'{self.build}/{self.hotspots_dir}/{cursor_name}.cursor'

    def cursor_file(self, cursor_name):
        return f'{paths.dist}/{paths.cursors_dir}/{cursor_name}'


arg_parser = ArgumentParser(description='Generate PNGs of all sizes from the theme SVG.')
arg_parser.add_argument('-s', '--sizes', nargs='+', action='store', dest='sizes', help='List of the available cursor sizes.')
arg_parser.add_argument('-p', '--prefix', action='store', dest='slice_prefix', help='Prefix to use for individual slice filenames (the "-a" parameter comes from the Latin word "ante" - sorry about that :D).')
arg_parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Enable extra debugging info.')
arg_parser.add_argument('-k', '--keep-tmp', action='store_true', dest='keep_tmp', help='Test mode: keeps temporary files for examination instead of deleting them when the job ends.')
args = arg_parser.parse_args()

sizes = args.sizes if args.sizes else default_sizes.split()
slice_prefix = args.slice_prefix if args.slice_prefix else ''
if args.debug:
    print('!DEBUG!')
    Logger().set_debug_mode(True)


for t in [f for f in scandir(f'{Paths.source}') if f.name.lower().endswith('.svg') and f.is_file()]:
    theme_name = ospath.splitext(t.name)[0]
    theme_dir = sub('[^A-Za-z0-9_-]', '-', theme_name)
    paths = Paths(theme_dir)

    print()
    report(f'Starting generating the "{theme_name}" cursor theme...')

    report('Removing old assets...')
    rmtree(paths.build, ignore_errors=True)
    rmtree(paths.dist, ignore_errors=True)

    # CLI command of the module
    # time $(./src/assets_generator.py -kt 'Mein Shadowed.svg' -b Mein-Shadowed -s 24 32 48)
    symlinks = CursorThemeAssetsGenerator().run(t.path, paths, sizes)

    makedirs(f'{paths.dist}/cursors', exist_ok=True)

    log.info('Writing theme files.')
    with open(f'{paths.dist}/cursor.theme', 'w') as f:
        f.write(f'[Icon Theme]\nName={theme_name}\nComment=Made using The G\'s cursor theme generator\nInherits={theme_name}')
        f.close()
    copyfile(f'{paths.dist}/cursor.theme', f'{paths.dist}/index.theme')

    for h in [f for f in scandir(f'{paths.build}/{paths.hotspots_dir}') if f.name.endswith('.cursor') and f.is_file()]:
        job_tokens = ['sort', h.path, '-o', h.path]
        job = run(job_tokens, stdout=DEVNULL, stderr=DEVNULL)
        cursor_name = ospath.splitext(h.name)[0]
        log.info(f'Creating the cursor file for {cursor_name}...')
        job_tokens = ['xcursorgen', h.path, paths.cursor_file(cursor_name)]
        job = run(job_tokens, stdout=DEVNULL, stderr=DEVNULL)
        if job.returncode > 0:
            log.error(f"Generating the {cursor_name} X11 cursor file failed. Command: {' '.join(job_tokens)}")

    for line in symlinks:
        symlink_source, *symlink_targets = line.split()
        for s in symlink_targets:
            s = paths.cursor_file(s)
            log.info(f'Creating symlink {s} pointing to {symlink_source}')
            try:
                symlink(symlink_source, s)
            except FileExistsError:
                log.error(f'File {s} already exists.')

    makedirs(paths.export, exist_ok=True)
    make_archive(f"{paths.export}/{theme_dir.lower()}-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}", 'zip', './dist/', theme_dir)

    if not args.keep_tmp:
        log.info('Removing the /buid/ directory.')
        rmtree(paths.build)

    report(f'Finished generating the {theme_name} cursor theme.')
