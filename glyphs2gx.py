#!/usr/bin/python

from __future__ import division
import glyphs2ufo.glyphslib
import glyphs2ufo.torf
import cu2qu.rf
import ufo2ft
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables._f_v_a_r import table__f_v_a_r, Axis, NamedInstance
from fontTools.ttLib.tables._g_v_a_r import table__g_v_a_r, GlyphVariation
import warnings

def build_ttfs (src):

	print "Loading Glyphs src `%s' into memory" % src
	if not hasattr(src, 'read'):
		src = open(src)
	dic = glyphs2ufo.glyphslib.load(src)
	del src

	print "Load into Robofab font"
	masters = glyphs2ufo.torf.to_robofab(dic)
	del dic

	print "Converting masters to compatible quadratics"
	cu2qu.rf.fonts_to_quadratic(masters, dump_stats=True)

	master_ttfs = []
	for master in masters:

		family = master.info.familyName
		style = master.info.styleName
		fullname = "%s-%s" % (family, style)

		print "Processing master", fullname

		print "Compiling master"
		ttfont = ufo2ft.compileTTF(master)
		outfile = fullname+".ttf"
		ttfont.save(outfile)
		master_ttfs.append(outfile)

	return master_ttfs, masters


def AddName(font, name):
	"""(font, "Bold") --> NameRecord"""
	nameTable = font.get("name")
	namerec = NameRecord()
	namerec.nameID = 1 + max([n.nameID for n in nameTable.names] + [256])
	namerec.string = name.encode("mac_roman")
	namerec.platformID, namerec.platEncID, namerec.langID = (1, 0, 0)
	nameTable.names.append(namerec)
	return namerec

def AddFontVariations(font, axes, instances):
	assert "fvar" not in font
	fvar = font["fvar"] = table__f_v_a_r()

	for tag in sorted(axes.keys()):
		axis = Axis()
		axis.axisTag = tag
		name, axis.minValue, axis.defaultValue, axis.maxValue = axes[tag]
		axis.nameID = AddName(font, name).nameID
		fvar.axes.append(axis)

	for name, coordinates in instances:
		inst = NamedInstance()
		inst.nameID = AddName(font, name).nameID
		inst.coordinates = coordinates
		fvar.instances.append(inst)

def GetCoordinates(font, glyphName):
	"""font, glyphName --> glyph coordinates as expected by "gvar" table

	The result includes four "phantom points" for the glyph metrics,
	as mandated by the "gvar" spec.
	"""
	glyphTable = font["glyf"]
	if glyphName not in glyphTable.glyphs: return None
	glyph = glyphTable[glyphName]
	if glyph.isComposite():
		coord = [c.getComponentInfo()[1][-2:] for c in glyph.components]
	else:
		coord = list(glyph.getCoordinates(glyphTable)[0])
	# Add phantom points for (left, right, top, bottom) positions.
	horizontalAdvanceWidth, leftSideBearing = font["hmtx"].metrics[glyphName]

	if not hasattr(glyph, 'xMin'):
		glyph.recalcBounds(glyphTable)
	leftSideX = glyph.xMin - leftSideBearing
	rightSideX = leftSideX + horizontalAdvanceWidth

	# XXX these are incorrect.  Load vmtx and fix.
	topSideY = glyph.yMax
	bottomSideY = -glyph.yMin

	coord.extend([(leftSideX, 0),
	              (rightSideX, 0),
	              (0, topSideY),
	              (0, bottomSideY)])
	return coord

def sub(al, bl):
	return [(ax-bx,ay-by) for (ax,ay),(bx,by) in zip(al,bl)]

def mul(l, mult):
	return [(x*mult,y*mult) for (x,y) in l]

def AddGlyphVariations(out, masters, locations, origin_idx):

	# Make copies for modification
	masters = masters[:]
	locations = [l.copy() for l in locations]

	# Move origin to front
	origin_master   = masters[origin_idx]
	origin_location = locations[origin_idx]
	del masters[origin_idx], locations[origin_idx]
	masters.insert(0, origin_master)
	locations.insert(0, origin_location)
	del origin_idx, origin_master, origin_location
	# Neutral is zero from now on

	axis_tags = locations[0].keys()

	# Normalize locations
	# https://github.com/behdad/fonttools/issues/313
	axis_mins = {tag:min(loc[tag] for loc in locations) for tag in axis_tags}
	axis_maxs = {tag:max(loc[tag] for loc in locations) for tag in axis_tags}
	axis_defaults = locations[0]
	for tag in axis_tags:
		minval,maxval,defaultval = axis_mins[tag],axis_maxs[tag],axis_defaults[tag]
		for l in locations:
			v = l[tag]
			if v == defaultval:
				v = 0
			elif v < defaultval:
				v = (v - defaultval) / (defaultval - minval)
			else:
				v = (v - defaultval) / (maxval - defaultval)
			l[tag] = v
	del axis_mins, axis_maxs, axis_defaults
	# Locations are normalized now

	# Find new axis mins and maxs
	axis_mins = {tag:min(loc[tag] for loc in locations) for tag in axis_tags}
	axis_maxs = {tag:max(loc[tag] for loc in locations) for tag in axis_tags}

	assert "gvar" not in out
	gvar = out["gvar"] = table__g_v_a_r()
	gvar.version = 1
	gvar.reserved = 0
	gvar.variations = {}

	for glyph in out.getGlyphOrder():

		allCoords = [GetCoordinates(m, glyph) for m in masters]
		coordsLen = len(allCoords[0])
		if (any(len(coords) != coordsLen for coords in allCoords)):
			warnings.warn("glyph %s has not the same number of "
			              "control points in all masters" % glyph)
			continue

		gvar.variations[glyph] = []

		# Subtract origin
		allCoords = [sub(coords, allCoords[0]) for coords in allCoords]

		# Add deltas for on-axis extremes
		for tag in axis_tags:
			for value in (axis_mins[tag], axis_maxs[tag]):
				if not value: continue
				loc = locations[0].copy()
				loc[tag] = value
				idx = locations.index(loc)
				loc, coords = locations[idx], allCoords[idx]
				if not coords:
					warnings.warn("Glyph not present in a master" + glyph)
					continue

				# Found master for axis extreme, add delta
				var = GlyphVariation({tag: (min(value, 0.), value, max(value, 0.))}, coords)
				gvar.variations[glyph].append(var)

def glyphs_ufo_get_weight(font):
	return font.lib.get(glyphs2ufo.torf.GLYPHS_PREFIX + 'weightValue', 100)

def glyphs_ufo_get_width(font):
	return font.lib.get(glyphs2ufo.torf.GLYPHS_PREFIX + 'widthValue',  100)

def build_gx(master_ttfs, master_ufos):
	print "Building GX"
	print "Loading TTF masters"
	master_fonts = [TTFont(f) for f in master_ttfs]

	# Find Regular master
	regular_idx = [s.endswith("Regular.ttf") for s in master_ttfs].index(True)
	print "Using %s as base font" % master_ttfs[regular_idx]
	regular = master_fonts[regular_idx]
	regular_weight = glyphs_ufo_get_weight(master_ufos[regular_idx])
	regular_width  = glyphs_ufo_get_width (master_ufos[regular_idx])

	# Set up master locations
	master_points = [{'wght': glyphs_ufo_get_weight(m) / regular_weight,
			  'wdth': glyphs_ufo_get_width (m) / regular_width}
			 for m in master_ufos]
	weights = [m['wght'] for m in master_points]
	widths  = [m['wdth'] for m in master_points]
	from pprint import pprint
	print "Master positions:"
	pprint(master_points)

	# Set up axes
	axes = {
		'wght': ('Weight', min(weights), weights[regular_idx], max(weights)),
		'wdth': ('Width',  min(widths),  widths [regular_idx], max(widths)),
	}

	# Set up named instances
	instances = {} # None for now

	gx = TTFont(master_ttfs[regular_idx])

	print "Setting up axes and instances"
	AddFontVariations(gx, axes, instances)

	print "Setting up glyph variations"
	AddGlyphVariations(gx, master_fonts, master_points, regular_idx)

	outname = master_ttfs[regular_idx].replace('-Regular', '')
	print "Saving GX font", outname
	gx.save(outname)


if __name__ == '__main__':
	import sys, pickle
	for src in sys.argv[1:]:

		pickle_file = src + '.pickle'
		try:
			c = pickle.load(open(pickle_file))
		except (IOError, EOFError):
			c = {}

		if not 'master_ttfs' in c or not 'master_ufos' in c:
			c['master_ttfs'], c['master_ufos'] = build_ttfs(src)

		#pickle.dump(c, open(pickle_file, 'wb'), pickle.HIGHEST_PROTOCOL)

		if not 'gx' in c:
			c['gx'] = build_gx(c['master_ttfs'], c['master_ufos'])
