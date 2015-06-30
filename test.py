#!/usr/bin/python

import glyphs2ufo.torf
import glyphs2ufo.glyphslib
import glyphs2ufo.torf
#from ufo2fdk import OTFCompiler
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.outlineTTF import OutlineTTFCompiler
from fontTools.ttLib import TTFont

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

def build_gx(master_ttfs, master_infos):
	print "Building GX"
	print "Loading TTF masters"
	master_fonts = [TTFont(f) for f in master_ttfs]


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

