#!/usr/bin/env python3
#
# SVGSlice
#
# Released under the GNU General Public License, version 2.
# Email Lee Braiden of Digital Unleashed at lee.b@digitalunleashed.com
# with any questions, suggestions, patches, or general uncertainties
# regarding this software.
#
# How it works:
# Basically, svgslice just parses an SVG file, looking for the tags that define the slices should be, and saves them in a list of rectangles. Next, it generates an XHTML file, passing that out stdout to Inkscape. This will be saved by inkscape under the name chosen in the save dialog. Finally, it calls inkscape again to render each rectangle as a slice.
# Currently, nothing fancy is done to layout the XHTML file in a similar way to the original document, so the generated pages is essentially just a quick way to see all of the slices in once place, and perhaps a starting point for more layout work.


from sys import exit
from os import makedirs
from shutil import copyfile
from xml.sax.handler import feature_namespaces
from xml.sax import make_parser, SAXParseException
from argparse import ArgumentParser
from threading import Thread, Semaphore
# from multiprocessing import Process, Semaphore
from inspect import cleandoc
from utils import report, print_progress
from layer_handler import SVGLayerHandler
from logger import Logger


log = Logger().get_logger(__name__)


class CursorThemeAssetsGenerator:
    max_threads = 4

    def main(self):
        arg_parser = ArgumentParser(description='Generate PNGs of all sizes from the theme SVG.')
        arg_parser.add_argument('-i', '--input', required=True, action='store', dest='input_file', help='Path (relative to the script root) to the source SVG file containing the graphics and attributes required for the cursor theme to be generated.')
        arg_parser.add_argument('-p', '--paths', required=True, action='store', dest='paths', help='Simple object containing the path structure for the script.')
        arg_parser.add_argument('-s', '--sizes', required=True, nargs='+', action='store', dest='sizes', help='List of the available cursor sizes.')
        arg_parser.add_argument('-a', '--prefix', action='store', dest='slice_prefix', help='Prefix to use for individual slice filenames (the "-a" parameter comes from the Latin word "ante" - sorry about that :D).')
        args = arg_parser.parse_args()

        self.run(args.input_file, args.paths, args.sizes, args.slice_prefix if args.slice_prefix else '')

    def run(self, input_file, paths, sizes, slice_prefix=''):
        self.job_count = 0
        self.symlinks = []

        report('Starting generating the cursor theme assets...')

        work_source = f'{paths.build}/{paths.source_file}'

        for size in sizes:
            makedirs(f'{paths.build}/{paths.pngs_dir}/{size}')  # make dirs for each size of the cursors
        makedirs(f'{paths.build}/{paths.hotspots_dir}')   # make dir for the hostspots files

        copyfile(input_file, work_source)

        # initialise results before actually attempting to parse the SVG file
        # svgBounds = SVGRect(0, 0, 0, 0)
        # rectList = []

        # Try to parse the svg file
        xmlParser = make_parser()
        xmlParser.setFeature(feature_namespaces, 0)

        # setup XML Parser with an SVGLayerHandler class as a callback parser ####
        svgLayerHandler = SVGLayerHandler()
        xmlParser.setContentHandler(svgLayerHandler)
        try:
            xmlParser.parse(work_source)
        except SAXParseException as e:
            msg = cleandoc(f'Error parsing SVG file \'{work_source}\' {e.getMessage()} [line {e.getLineNumber()}, col {e.getColumnNumber()}]. If you\'re seeing this within inkscape, it probably indicates a bug that should be reported.')
            log.error(msg)
            exit(msg)

        # verify that the svg file actually contained some rectangles.
        rects_count = len(svgLayerHandler.svg_rects)
        if rects_count == 0:
            msg = cleandoc("""
                No slices were found in this SVG file. You need to add a layer called
                "slices", and draw rectangles on it to represent the areas that should
                be saved as slices. It helps when drawing these rectangles if you make
                them translucent.

                Use Inkscape's built-in XML editor (Ctrl + Shift + X) to name these
                slices using the "id" field of Inkscape's built-in XML editor - that
                name will be reflected in the slice filenames. Also, use it to
                add/fill/edit the "hotspot" and "symlinks" attributes.

                Please remember to HIDE the slices layer before exporting, so that the
                rectangles themselves are not drawn in the final image slices.""")
            log.error(msg)
            exit(msg)
        else:
            report("Parsing SVG successful.")
            self.job_count = rects_count * len(sizes)

        # svgLayerHandler.generateXHTMLPage()

        report('Starting looping through slices...')
        semaphore = Semaphore(self.max_threads)
        workers = []
        # loop through each slice rectangle, and render a PNG image for it
        for i, size in enumerate(sizes):
            for j, rect in enumerate(svgLayerHandler.svg_rects):
                k = int(i * j + j)
                workers.append(Thread(target=self.job, args=(semaphore, k, rect.generateAssets, size, paths, slice_prefix)))
                # workers.append(Process(target=self.job, args=(semaphore, rect.generateAssets, size, paths, slice_uri)))
        for w in workers:
            w.start()
        for w in workers:
            w.join()

        print(' ' * 160, end='\r')  # clear the progress bar
        report('Finished generating the cursor theme assets.')

        return self.symlinks

    def job(self, semaphore, index, process, *args):
        with semaphore:
            print_progress(index, self.job_count)
            data = process(*args)
            if data:
                self.symlinks.append(data)


if __name__ == '__main__':
    CursorThemeAssetsGenerator().main()
