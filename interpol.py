#!/usr/bin/python

import sys
import cairo
import pprint
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

class AccPen(BasePen):
	def __init__(self, glyphset):
		BasePen.__init__(self, glyphset)
		self.contours = []
	def _moveTo(self, pt):
		self.contours.append([])
		self.contours[-1].append(pt)
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

def draw_lines(cr, points, widths):
	cr.new_sub_path()
	for i,p in enumerate(points):
		cr.line_to(p[0] + (1000 - widths[i])/2., p[1])

master_colors = [
(1,0,0),
(0,1,0),
(0,0,1),
(1,0,1),
(1,1,0),
(0,1,1),
]

family = "NotoSansCJK"
weights = ["Regular", "DemiLight", "Light", "Thin"]
ext = "otf"

fonts = [TTFont("%s-%s.%s" % (family, weight, ext)) for weight in weights]
glyphsets = [f.getGlyphSet() for f in fonts]
glyphs = fonts[0].getGlyphOrder()
assert all(glyphs == f.getGlyphOrder() for f in fonts)

upem = fonts[0]['head'].unitsPerEm
ascent = fonts[0]['hhea'].ascent
descent = -fonts[0]['hhea'].descent

n = 0
if len(sys.argv) > 1:
	n = int(sys.argv[1])

for g in glyphs[n:]:
	outlines = [glyphset[g] for glyphset in glyphsets]
	drawings = []
	widths = []
	for i,outline in enumerate(outlines):
		pen=AccPen(glyphsets[i])
		outline.draw(pen)
		drawings.append(pen.contours)
		widths.append(outline.width)
	print g
	surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 7*72,7*72)
	cr = cairo.Context(surface)
	cr.translate(.5*72, .5*72)
	cr.scale(1,-1)
	cr.scale(6*72./upem, 6*72./upem)
	cr.translate(0, -ascent)
	cr.set_source_rgb(1, 1, 1)
	cr.paint()
	cr.set_line_width(upem/1000.)
	for i,drawing in enumerate(drawings):
		cr.save()
		cr.translate((1000 - widths[i])/2.,0)
		for contour in drawing:
			cr.new_sub_path()
			for op in contour:
				if len(op) == 2:
					cr.line_to(*op)
				else:
					cr.curve_to(*sum(op,()))
			cr.close_path()
		cr.set_source_rgba(*master_colors[i]+(.04,))
		cr.fill_preserve()
		cr.set_source_rgba(*master_colors[i]+(.4,))
		cr.stroke()
		cr.restore()
	if all(drawing_compat(drawings[0], drawing) for drawing in drawings):
		for contours in zip(*drawings):
			for ops in zip(*contours):
				if len(ops[0]) == 2:
					draw_lines(cr, ops, widths)
				else:
					for points in zip(*ops):
						draw_lines(cr, points, widths)
		cr.set_source_rgb(1,0,0)
		cr.stroke()
	surface.write_to_png("%s.png" % g)
