#!/usr/bin/python

import glyphs2ufo.torf
f = open("NotoSansUI-RomanMM.glyphs")

import glyphs2ufo.glyphslib
d = glyphs2ufo.glyphslib.load(f)

import glyphs2ufo.torf
masters = glyphs2ufo.torf.to_robofab(d)

from ufo2fdk import OTFCompiler
compiler = OTFCompiler() 
reports = compiler.compile(masters[0], "a.otf", autohint=False)
print reports["makeotf"]

