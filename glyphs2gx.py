#!/usr/bin/python

import glyphs2ufo.torf
import glyphs2ufo.glyphslib
import glyphs2ufo.torf
#from ufo2fdk import OTFCompiler
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.outlineTTF import OutlineTTFCompiler
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
	master_infos = dic['fontMaster']
	del dic

	master_ttfs = []
	for master in masters:

		family = master.info.familyName
		style = master.info.styleName
		fullname = "%s-%s" % (family, style)

		print "Processing master", fullname

		#compiler = OTFCompiler()
		#reports = compiler.compile(master, fullname+".otf", autohint=False)
		#print reports

		print "Converting outlines to quadratic"
		for glyph in master:
			     glyphCurvesToQuadratic(glyph)

		print "Compiling master"
		compiler = OutlineTTFCompiler(master, fullname+".ttf")
		compiler.compile()
		master_ttfs.append(fullname+".ttf")

	return master_ttfs, master_infos


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
    glyph = glyphTable[glyphName]
    if glyph.isComposite():
        glyph.recalcBounds(glyphTable)
        coord = [c.getComponentInfo()[1][-2:] for c in glyph.components]
    else:
        coord = [c for c in glyph.getCoordinates(glyphTable)[0].copy()]
    # Add phantom points for (left, right, top, bottom) positions.
    horizontalAdvanceWidth, leftSideBearing = font["hmtx"].metrics[glyphName]

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

def AddGlyphVariations(out, masters, locations, neutral):
    assert "gvar" not in out
    gvar = out["gvar"] = table__g_v_a_r()
    gvar.version = 1
    gvar.reserved = 0
    gvar.variations = {}

    return

    for glyph in out.getGlyphOrder():
        regularCoord = GetCoordinates(regular, glyph)
        thinCoord = GetCoordinates(thin, glyph)
        blackCoord = GetCoordinates(black, glyph)
        if not regularCoord or not blackCoord or not thinCoord:
            warnings.warn("glyph %s not present in all input fonts" %
                          glyph)
            continue
        if (len(regularCoord) != len(blackCoord) or
            len(regularCoord) != len(thinCoord)):
            warnings.warn("glyph %s has not the same number of "
                          "control points in all input fonts" % glyph)
            continue
        thinDelta = []
        blackDelta = []
        for ((regX, regY), (blackX, blackY), (thinX, thinY)) in \
                zip(regularCoord, blackCoord, thinCoord):
            thinDelta.append(((thinX - regX, thinY - regY)))
            blackDelta.append((blackX - regX, blackY - regY))
        thinVar = GlyphVariation({"wght": (-1.0, -1.0, 0.0)}, thinDelta)
        blackVar = GlyphVariation({"wght": (0.0, 1.0, 1.0)}, blackDelta)
        gvar.variations[glyph] = [thinVar, blackVar]

def build_gx(master_ttfs, master_infos):
	print "Building GX"
	print "Loading TTF masters"
	master_fonts = [TTFont(f) for f in master_ttfs]

	# Find Regular master
	regular_idx = [s.endswith("Regular.ttf") for s in master_ttfs].index(True)
	print "Using %s as base font" % master_ttfs[regular_idx]
	regular = master_fonts[regular_idx]
	regular_weight = float(master_infos[regular_idx]['weightValue'])
	regular_width = float(master_infos[regular_idx]['widthValue'])

	# Set up master locations
	master_points = [{'wght': m['weightValue'] / regular_weight,
			  'wdth': m['widthValue']  / regular_width}
			 for m in master_infos]
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

		if not 'master_ttfs' in c or not 'master_infos' in c:
			c['master_ttfs'], c['master_infos'] = build_ttfs(src)

		pickle.dump(c, open(pickle_file, 'wb'), pickle.HIGHEST_PROTOCOL)

		if not 'gx' in c:
			c['gx'] = build_gx(c['master_ttfs'], c['master_infos'])
