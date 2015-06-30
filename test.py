#!/usr/bin/python

import glyphs2ufo.torf
import glyphs2ufo.glyphslib
import glyphs2ufo.torf
#from ufo2fdk import OTFCompiler
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.outlineTTF import OutlineTTFCompiler

def build (src):

	print "Loading Glyphs src `%s' into memory" % src
	if not hasattr(src, 'read'):
		src = open(src)
	dic = glyphs2ufo.glyphslib.load(src)
	del src

	print "Load into Robofab font"
	masters = glyphs2ufo.torf.to_robofab(dic)
	del dic

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

if __name__ == '__main__':
	import sys
	for src in sys.argv[1:]:
		build (src)
