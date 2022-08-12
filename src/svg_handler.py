#!/usr/bin/env python3


from sys import exit
from xml.sax import handler
from svg_rect import SVGRect
from logger import Logger


log = Logger().get_logger(__name__)


class SVGHandler(handler.ContentHandler):
    """Base class for SVG parsers"""

    def __init__(self):
        self.pageBounds = SVGRect(0, 0, 0, 0)

    def isFloat(self, stringVal):
        try:
            return (float(stringVal), True)[1]
        except (ValueError, TypeError):
            return False

    def parseCoordinates(self, val):
        """Strips the units from a coordinate, and returns just the value."""
        if val.endswith('px'):
            val = float(val.rstrip('px'))
        elif val.endswith('pt'):
            val = float(val.rstrip('pt'))
        elif val.endswith('cm'):
            val = float(val.rstrip('cm'))
        elif val.endswith('mm'):
            val = float(val.rstrip('mm'))
        elif val.endswith('in'):
            val = float(val.rstrip('in'))
        elif val.endswith('%'):
            val = float(val.rstrip('%'))
        elif self.isFloat(val):
            val = float(val)
        else:
            log.error(f'Coordinate value {val} has unrecognised units.  Only px, pt, cm, mm, and in units are currently supported.')
            exit(1)
        return val

    def startElement_svg(self, name, attrs):
        """Callback hook which handles the start of an svg image"""
        # E('startElement_svg called')
        width = attrs.get('width', None)
        height = attrs.get('height', None)
        self.pageBounds.x2 = self.parseCoordinates(width)
        self.pageBounds.y2 = self.parseCoordinates(height)

    def endElement(self, name):
        """General callback for the end of a tag"""
        # E('Ending element "%s"' % name)
        return
