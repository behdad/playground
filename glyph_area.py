"""Calculate the area of a glyph."""


from robofab.objects.objectsRF import RPoint
from robofab.world import OpenFont

import sys


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


def glyph_area(glyph, units_per_em):
  area = 0
  for contour in glyph:
    last_on, off = contour.points[0], []
    for i in range(len(contour.points)):
      cur = contour.points[(i + 1) % len(contour.points)]

      if cur.type == 'offcurve':
        off.append(cur)
        continue

      if cur.type == 'qcurve':
        assert len(off), '"qcurve"-type point follows on-curve point'
        for i in range(len(off) - 1):
          cur_off, next_off = off[i], off[i + 1]
          cur_on = interpolate(cur_off, next_off, 0.5)
          area += quadratic_curve_area(last_on, cur_off, cur_on)
          area += polygon_area(last_on, cur_on)
          last_on = cur_on
        next_off = off[len(off) - 1]
        area += quadratic_curve_area(last_on, next_off, cur)

      elif cur.type == 'curve':
        assert len(off) == 2, ('"curve"-type point doesn\'t follow exactly two '
          'off-curve points')
        area += cubic_curve_area(last_on, off[0], off[1], cur)

      area += polygon_area(last_on, cur)
      last_on, off = cur, []

  return abs(area) / (glyph.width * units_per_em)


def main(argv):
  font = OpenFont(argv[1])
  print glyph_area(font[argv[2]], font.info.unitsPerEm)


if __name__ == '__main__':
  main(sys.argv)
