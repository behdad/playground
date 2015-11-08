"""Calculate the area of a glyph."""

import math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from collections import namedtuple

def struct (name, members):
	cls = namedtuple (name, members)
	cls.__repr__ = lambda self: "%s(%s)" % (name, ','.join(str(s) for s in self))
	return cls

class P (struct ('P', ('x', 'y'))):
	pass


def distance(p0, p1):
  return math.hypot(p0.x - p1.x, p0.y - p1.y)

def interpolate(p0, p1, t):
  return P(p0.x * (1 - t) + p1.x * t, p0.y * (1 - t) + p1.y * t)


def polygon_area(p0, p1):
  return (p1.x - p0.x) * (p1.y + p0.y) * 0.5


def quadratic_curve_area(p0, p1, p2):
  new_p2 = interpolate(p2, p1, 2.0 / 3)
  new_p1 = interpolate(p0, p1, 2.0 / 3)
  return cubic_curve_area(p0, new_p1, new_p2, p2)


def cubic_curve_area(p0, p1, p2, p3):
  x0, y0 = p0.x, p0.y
  x1, y1 = p1.x - x0, p1.y - y0
  x2, y2 = p2.x - x0, p2.y - y0
  x3, y3 = p3.x - x0, p3.y - y0
  return (
      x1 * (   -   y2 -   y3) +
      x2 * (y1        - 2*y3) +
      x3 * (y1 + 2*y2       )
  ) * 0.15


class AreaPen(BasePen):

	def __init__(self, glyphset):
		BasePen.__init__(self, glyphset)
		self.value = 0

	def _moveTo(self, p0):
		pass

	def _lineTo(self, p1):
		p0 = self._getCurrentPoint()
		self.value += polygon_area(P(*p0), P(*p1))

	def _curveToOne(self, p1, p2, p3):
		p0 = self._getCurrentPoint()
		self.value += cubic_curve_area(P(*p0), P(*p1), P(*p2), P(*p3))
		self.value += polygon_area(P(*p0), P(*p3))


class PerimeterPen(BasePen):

	def __init__(self, glyphset):
		BasePen.__init__(self, glyphset)
		self.value = 0

	def _moveTo(self, p0):
		pass

	def _lineTo(self, p1):
		p0 = self._getCurrentPoint()
		self.value += distance(P(*p0), P(*p1))

	def _curveToOne(self, p1, p2, p3):
		p0 = self._getCurrentPoint()
		# TODO very rudimentary hack
		arch = distance(P(*p0), P(*p3))
		box = distance(P(*p0), P(*p1)) + distance(P(*p1), P(*p2)) + distance(P(*p2), P(*p3))
		self.value += (arch + box) / 2.

def pen_value(glyphset, glyph, Pen):
	pen = Pen(glyphset)
	glyph.draw(pen)
	return pen.value


class PerContourPen(BasePen):

	def __init__(self, glyphset, Pen):
		BasePen.__init__(self, glyphset)
		self._glyphset = glyphset
		self._Pen = Pen
		self.value = []

	# XXX port to pen protocol proper

	def _moveTo(self, p0):
		self.value.append(self._Pen(self._glyphset))
		self.value[-1].moveTo(p0)

	def _lineTo(self, p1):
		self.value[-1].lineTo(p1)

	def _curveToOne(self, p1, p2, p3):
		self.value[-1].curveTo(p1, p2, p3)


def per_contours(glyphs, glyph, Pen):
	def PenClosure(glyphs):
		return PerContourPen(glyphs, Pen)
	return pen_value(glyphs, glyph, PenClosure)

