#!/usr/bin/python

from fontTools import ttLib
from fontTools import cffLib
import sys

def unpeel(filename):
	font = ttLib.TTFont(filename)
	cffFont = font['CFF '].cff.topDictIndex[0]
	charstrings = cffFont.CharStrings
	glyphs = font.getGlyphOrder()
	items = [charstrings[glyph] for glyph in glyphs]
	compiler = cffLib.CharStringsCompiler(items, None, None)
	compiler.toFile(sys.stdout)

if __name__ == '__main__':
	for filename in sys.argv[1:]:
		unpeel(filename)
