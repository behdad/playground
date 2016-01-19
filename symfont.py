"""Calculate the area of a glyph."""

import sympy as sp

n = 3 # Max Bezier degree; 3 for cubic, 2 for quadratic

t, x, y = sp.symbols('t x y', real=True)
Psymbol = sp.symbols('P')

P = tuple(sp.symbols('P[:%d][:2]' % (n+1), real=True))
P = tuple(P[2*i:2*(i+1)] for i in range(len(P) // 2))

# Cubic Berstein basis functions
BinomialCoefficient = [(1, 0)]
for i in range(1, n+1):
	last = BinomialCoefficient[-1]
	this = tuple(last[j-1]+last[j] for j in range(len(last)))+(0,)
	BinomialCoefficient.append(this)
BinomialCoefficient = tuple(tuple(item[:-1]) for item in BinomialCoefficient)

BersteinPolynomial = tuple(
	tuple(c * t**i * (1-t)**(n-i) for i,c in enumerate(coeffs))
	for n,coeffs in enumerate(BinomialCoefficient))

BezierCurve = tuple(
	tuple(sum(P[i][j]*berstein for i,berstein in enumerate(bersteins))
		for j in range(2))
	for n,bersteins in enumerate(BersteinPolynomial))

def green(f, Bezier=BezierCurve[n]):
	f1 = sp.integrate(f, y)
	f2 = f1.replace(y, Bezier[1]).replace(x, Bezier[0])
	return sp.integrate(f2 * sp.diff(Bezier[0], t), (t, 0, 1))

def lambdify(f):
	return sp.lambdify(Psymbol, f)

b = ((0,0), (0,1), (1,1), (1,0))
b1 = ((0,0), (0,2), (1,2), (1,0))
b2 = ((0,0), (0,1), (2,1), (2,0))
b3 = ((0,0), (0,2), (2,2), (2,0))
b100 = ((100,0), (100,1), (101,1), (101,0))

b4 = ((-1,0), (-1,1), (1,1), (1,0))
b5 = ((-2,0), (-2,1), (2,1), (2,0))

area = green(1)
area_f = lambdify(area)
print "area", area_f

xmom1 = green(x)
xmom1_f = lambdify(xmom1)
xmean_f = lambda P: xmom1_f(P) / area_f(P)
print "xmean", xmean_f

ymom1 = green(y)
ymom1_f = lambdify(ymom1)
ymean_f = lambda P: ymom1_f(P) / area_f(P)
print "ymean", ymean_f

# https://en.wikipedia.org/wiki/Second_moment_of_area

xmom2 = green(x**2)
xmom2_f = lambdify(xmom2)
def xvar_f(P):
	# https://en.wikipedia.org/wiki/Central_moment#Relation_to_moments_about_the_origin
	#  Var(X) = E[X^2] - E[X]^2
	area = area_f(P)
	xmom1 = xmom1_f(P)
	xmom2 = xmom2_f(P)
	xmean = xmom1 / area
	xvar = xmom2 / area
	return xvar - xmean**2
print "xvar", xvar_f

ymom2 = green(y**2)
ymom2_f = lambdify(ymom2)
def yvar_f(P):
	# https://en.wikipedia.org/wiki/Central_moment#Relation_to_moments_about_the_origin
	#  Var(X) = E[X^2] - E[X]^2
	area = area_f(P)
	ymom1 = ymom1_f(P)
	ymom2 = ymom2_f(P)
	ymean = ymom1 / area
	yvar = ymom2 / area
	return yvar - ymean**2
print "yvar", yvar_f


xymom = green(x * y)
xymom_f = lambdify(xymom)
def corr_f(P):
	# https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient
	#  Covar(X,Y) = ( E[X.Y] - E[X]E[Y] ) / (sigma_X.sigma_Y)
	area = area_f(P)
	xmom1 = xmom1_f(P)
	ymom1 = ymom1_f(P)
	xmean = xmom1 / area
	ymean = ymom1 / area
	covar = xymom_f(P) / area
	xsigma = xvar_f(P)**.5
	ysigma = yvar_f(P)**.5
	return (covar - xmean*ymean) / (xsigma*ysigma)
print "corr", corr_f

#from sympy import AppliedPredicate, Q
#from sympy.assumptions.assume import global_assumptions

def main(argv):
	for filename in argv[1:]:
		font = TTFont(filename)
		foolAround(font.getGlyphSet(), font['head'].unitsPerEm)

if __name__ == '__main__':
	import sys
	main(sys.argv)
