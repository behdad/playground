"""Calculate the area of a glyph."""

from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from collections import namedtuple

def struct (name, members):
	cls = namedtuple (name, members)
	cls.__repr__ = lambda self: "%s(%s)" % (name, ','.join(str(s) for s in self))
	return cls

class P (struct ('P', ('x', 'y'))):
	pass


def interpolate(p0, p1, t):
  return RPoint(p0.x * (1 - t) + p1.x * t, p0.y * (1 - t) + p1.y * t)


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
		self.area = 0

	def _moveTo(self, p0):
		pass

	def _lineTo(self, p1):
		p0 = self._getCurrentPoint()
		self.area += polygon_area(P(*p0), P(*p1))

	def _curveToOne(self, p1, p2, p3):
		p0 = self._getCurrentPoint()
		self.area += cubic_curve_area(P(*p0), P(*p1), P(*p2), P(*p3))
		self.area += polygon_area(P(*p0), P(*p3))


def glyph_area(glyphset, glyph):
	pen = AreaPen(glyphset)
	glyph.draw(pen)
	return pen.area


def main(argv):
  font = OpenFont(argv[1])
  print glyph_area(font[argv[2]])


if __name__ == '__main__':
  import sys
  main(sys.argv)
