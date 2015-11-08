#!/usr/bin/python

from fontTools.ttLib import TTFont
from pens import *

def foolAround(glyphs, upem):
	print 'upem', upem
	for glyph_name in ['e', 'o', 'I', 'slash', 'E', 'zero', 'eight']:
		print
		print "glyph", glyph_name
		glyph = glyphs[glyph_name]
		area = glyph_area(glyphs, glyph)
		peri = glyph_perimeter(glyphs, glyph)
		stem = area / peri
		print "stem %g area %g peri %g" % (stem, area, peri)

def main(argv):
	for filename in argv[1:]:
		font = TTFont(filename)
		foolAround(font.getGlyphSet(), font['head'].unitsPerEm)

if __name__ == '__main__':
	import sys
	main(sys.argv)
