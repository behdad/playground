#!/usr/bin/python

from fontTools.ttLib import TTFont

def foolAround(glyphs):
	for glyph in ['e', 'o', 'I', 'slash']:
		print "Glyph:", glyph
		area = 


if __name__ == '__main__':
	import sys
	for filename in sys.argv[1:]:
		font = TTFont(filename)
		foolAround(font.getGlyphSet())
