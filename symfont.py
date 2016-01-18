"""Calculate the area of a glyph."""

import sympy as sp

t, x, y = sp.symbols('t x y', real=True)
x0,x1,x2,x3,y0,y1,y2,y3 = sp.symbols ('x:4 y:4', real=True)

# Cubic Berstein basis functions
B = [t**i * (1-t)**(3 - i) for i in range(3+1)]
xt = sum(xi * Bi for xi,Bi in zip([x0,x1,x2,x3],B))
yt = sum(yi * Bi for yi,Bi in zip([y0,y1,y2,y3],B))


def green(f):
	f1 = sp.integrate (f, y)
	f2 = f1.replace(y, yt).replace(x, xt)
	return sp.integrate (f2 * sp.diff(xt, t), (t, 0, 1))

area = green(1)
print "area", area

xmom1 = green(x)
xmean = xmom1 / area
print "xmean", xmean

ymom1 = green(y)
ymean = ymom1 / area
print "ymean", ymean

xymom = green(x * y)
corr = xymom
print "corr", corr

#from sympy import AppliedPredicate, Q
#from sympy.assumptions.assume import global_assumptions
