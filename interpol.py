#!/usr/bin/python

import sys
import pprint
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

class AccPen(BasePen):
	contours = []
	def _moveTo(self, pt):
		self.contours.append([])
	def _lineTo(self, pt):
		self.contours[-1].append(pt)
	def _curveToOne(self, pt1, pt2, pt3):
		self.contours[-1].append((pt1, pt2, pt3))
	def _closePath(self):
		pass

def drawing_compat(d0, d1):
	if len(d0) != len(d1):
		return False
	for c0,c1 in zip(d0,d1):
		if len(c0) != len(c1):
			return False
		for o0, o1 in zip(c0, c1):
			if len(o0) != len(o1):
				return False
	return True

family = "NotoSansCJK"
weights = ["Thin", "Regular", "Black"]
ext = "otf"

fonts = [TTFont("%s-%s.%s" % (family, weight, ext)) for weight in weights]
glyphsets = [f.getGlyphSet() for f in fonts]
glyphs = fonts[0].getGlyphOrder()[1:]
assert all(glyphs == f.getGlyphOrder()[1:] for f in fonts)
for g in glyphs:
	print g
	outlines = [glyphset[g] for glyphset in glyphsets]
	drawings = []
	for i,outline in enumerate(outlines):
		pen=AccPen(glyphsets[i])
		outline.draw(pen)
		drawings.append(pen.contours)
	assert all(drawing_compat(drawings[0], drawing) for drawing in drawings)
