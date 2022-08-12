#!/usr/bin/env python3


from sys import stdout
from svg_rect import SVGRect
from svg_handler import SVGHandler
from logger import Logger


log = Logger().get_logger(__name__)


class SVGLayerHandler(SVGHandler):
    """Parses an SVG file, extracing slicing rectangles from a "slices" layer"""

    def __init__(self):
        SVGHandler.__init__(self)
        self.svg_rects = []
        self.layer_nests = 0

    def inSlicesLayer(self):
        return (self.layer_nests >= 1)

    def add(self, rect):
        """Adds the given rect to the list of rectangles successfully parsed"""
        self.svg_rects.append(rect)

    def startElement_layer(self, name, attrs):
        """Callback hook for parsing layer elements

        Checks to see if we're starting to parse a slices layer, and sets the appropriate flags.  Otherwise, the layer will simply be ignored."""
        # log.info(f"found layer: name='{name}' id='{attrs['id']}'")
        if attrs.get('inkscape:groupmode', None) == 'layer':
            if self.inSlicesLayer() or attrs['inkscape:label'] == 'slices':
                self.layer_nests += 1

    def endElement_layer(self, name):
        """Callback for leaving a layer in the SVG file

        Just undoes any flags set previously."""
        # log.info(f"leaving layer: name='{name}'")
        if self.inSlicesLayer():
            self.layer_nests -= 1

    def startElement_rect(self, name, attrs):
        """Callback for parsing an SVG rectangle

        Checks if we're currently in a special "slices" layer using flags set by startElement_layer().  If we are, the current rectangle is considered to be a slice, and is added to the list of parsed
        rectangles.  Otherwise, it will be ignored."""
        if self.inSlicesLayer():
            x1 = self.parseCoordinates(attrs['x'])
            y1 = self.parseCoordinates(attrs['y'])
            x2 = self.parseCoordinates(attrs['width']) + x1
            y2 = self.parseCoordinates(attrs['height']) + y1
            name = attrs['id']
            hotspot = attrs['hotspot'] if 'hotspot' in attrs else None
            symlinks = attrs['symlinks'] if 'symlinks' in attrs else None
            rect = SVGRect(x1, y1, x2, y2, name, hotspot, symlinks)
            self.add(rect)

    def startElement(self, name, attrs):
        """Generic hook for examining and/or parsing all SVG tags"""
        # log.info(f"Beginning element 'name'")
        if name == 'svg':
            self.startElement_svg(name, attrs)
        elif name == 'g':
            # inkscape layers are groups, I guess, hence 'g'
            self.startElement_layer(name, attrs)
        elif name == 'rect':
            self.startElement_rect(name, attrs)

    def endElement(self, name):
        """Generic hook called when the parser is leaving each SVG tag"""
        # log.info(f"Ending element 'name'")
        if name == 'g':
            self.endElement_layer(name)

    def generateXHTMLPage(self):
        """Generates an XHTML page for the SVG rectangles previously parsed."""
        write = stdout.write
        write('<?xml version="1.0" encoding="UTF-8"?>\n')
        write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd">\n')
        write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n')
        write('    <head>\n')
        write('        <title>Sample SVGSlice Output</title>\n')
        write('    </head>\n')
        write('    <body>\n')
        write('        <p>Sorry, SVGSlice\'s XHTML output is currently very basic.  Hopefully, it will serve as a quick way to preview all generated slices in your browser, and perhaps as a starting point for further layout work.  Feel free to write it and submit a patch to the author :)</p>\n')

        write('        <p>')
        for rect in self.svg_rects:
            write('            <img src="%s" alt="%s (please add real alternative text for this image)" longdesc="Please add a full description of this image" />\n' % (sliceprefix + rect.name + '.png', rect.name))
        write('        </p>')

        write('<p><a href="http://validator.w3.org/check?uri=referer"><img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0!" height="31" width="88" /></a></p>')

        write('    </body>\n')
        write('</html>\n')
