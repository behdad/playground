#!/usr/bin/python

from fontTools.ttLib import TTFont
from pens import *

def foolAround(glyphs, upem):
	print 'upem', upem
	for glyph_name in ['e', 'o', 'I', 'slash', 'E', 'zero', 'eight', 'minus', 'equal']:
		print
		print "glyph", glyph_name
		glyph = glyphs[glyph_name]
		area = abs(pen_value(glyphs, glyph, AreaPen))
		peri = pen_value(glyphs, glyph, PerimeterPen)

		# naive stem
		stem_naive = area / peri * 2.
		print "stem0 %g area %g peri %g" % (stem_naive, area, peri)

		contour_areas = [c.value for c in per_contours(glyphs, glyph, AreaPen)]
		sign = -1 if sum(contour_areas) < 0 else +1
		contour_areas = [sign * a for a in contour_areas]
		positive = len([a for a in contour_areas if a > 0])
		negative = len([a for a in contour_areas if a < 0])
		#print positive, negative

		#contour-aware stem
		a = positive - negative
		b = -peri/2.
		c = area
		if a:
			delta = b*b - 4*a*c
			stem_aware = (-b - math.sqrt(delta)) / (2*a)
		else:
			stem_aware = -c / b
		print "stem1 %g" % stem_aware

def main(argv):
	for filename in argv[1:]:
		font = TTFont(filename)
		foolAround(font.getGlyphSet(), font['head'].unitsPerEm)

if __name__ == '__main__':
	import sys
	main(sys.argv)
