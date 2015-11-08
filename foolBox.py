#!/usr/bin/python

from fontTools.ttLib import TTFont
from glyph_area import glyph_area

def foolAround(glyphs, upem):
	print 'upem', upem
	for glyph_name in ['e', 'o', 'I', 'slash']:
		print
		print "glyph", glyph_name
		glyph = glyphs[glyph_name]
		area = glyph_area(glyphs, glyph)
		print "area", area

def main(argv):
	for filename in argv[1:]:
		font = TTFont(filename)
		foolAround(font.getGlyphSet(), font['head'].unitsPerEm)

if __name__ == '__main__':
	import sys
	main(sys.argv)
