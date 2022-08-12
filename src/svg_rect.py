#!/usr/bin/env python3
#
# SVGSlice
#
# Released under the GNU General Public License, version 2.
# Email Lee Braiden of Digital Unleashed at lee.b@digitalunleashed.com
# with any questions, suggestions, patches, or general uncertainties
# regarding this software.


from sys import exit
from subprocess import DEVNULL, run
from re import sub
from pathlib import Path
from logger import Logger


log = Logger().get_logger(__name__)


class SVGRect:
    """Manages a simple rectangular area, along with certain attributes such as a name"""
    base_size = 24

    def __init__(self, x1, y1, x2, y2, name=None, hotspot=None, symlinks=None, group=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.name = name
        self.hotspot = hotspot
        self.symlinks = symlinks
        # log.info(f'New SVGRect: #{name} ({vars(self)})')

    def generateAssets(self, size, paths, slice_prefix):
        export_file = paths.export_file(self.name, size, slice_prefix)
        if Path(export_file).is_file():
            log.error(f'Export file {export_file} already exists.')
            return ''

        log.info(f'Saving slice as {export_file}')
        # inkscape -w 32 -h 32 -i wait-05 -o ./build/Mein-Shadowed/pngs/32/wait-05.png --export-type=png ./build/Mein-Shadowed/cursors.svg
        job_tokens = ['inkscape', '-w', size, '-h', size, '-i', self.name, '-o', export_file, '--export-type=png', paths.export_source]
        # Inkscape AppImage complains a lot about missing libraries, so I silenced it
        # job = run(job_tokens, check=True, text=True)
        job = run(job_tokens, check=True, text=True, stdout=DEVNULL, stderr=DEVNULL)
        if job.returncode > 0:
            msg = f'ABORTED: Inkscape failed to render the size {size} slice of {export_file}.'
            log.error(msg)
            exit(msg)

        # # Optional; needs optinpng (apt install optipng in Ubuntu)
        # log.info(f'Optimizing {export_file}.')
        # job = run(['optipng', '-o2', '-quiet', export_file], stdout=DEVNULL, stderr=DEVNULL)
        # if job.returncode > 0:
        #     log.error(f'Optimization of {export_file} failed.')

        cursor_name = sub(r'-\d+$', '', self.name)
        if self.hotspot:
            hotspot = self.xtrapolate(self.hotspot, size)
            hotspots_file = paths.hotspots_file(cursor_name)
            log.info(f'Writing hotspot "{size} {hotspot} {export_file}" to hotspots file {hotspots_file}')
            with open(hotspots_file, 'a') as f:
                line = f'{size} {hotspot} {export_file}'
                if cursor_name != self.name:
                    line += ' 60'
                f.write(f'{line}\n')
                f.close()

        return f'{cursor_name} {self.symlinks}' if int(size) == self.base_size and self.symlinks else ''

    def xtrapolate(self, base_xy, size):
        size = int(size)

        if size == self.base_size:
            return base_xy

        coef = size / self.base_size
        x, y = map(lambda x: round(int(x) * coef), base_xy.split())
        return f'{x} {y}'
