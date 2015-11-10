#!/usr/bin/python
# -*- coding:utf8 -*-

# Copyright 2014 Behdad Esfahbod <behdad@google.com>

# A slides file should populate the variable slides with
# a list of tuples.  Each tuple should have:
#
#	- Slide content
#	- User data
#	- Canvas width
#	- Canvas height
#
# Slide content can be a string, a list of strings,
# a function returning one of those, or a generator
# yielding strings.  The user data should be a dictionary or
# None, and is both used to communicate options to the
# renderer and to pass extra options to the theme functions.
#
# A function-based slide content will be passed a renderer object.
# Renderer is an object similar to a cairo.Context and
# pangocairo.CairoContext but has its own methods too.
# The more useful of them here are put_text, put_image, and
# set_allocation.  See their pydocs.

from __future__ import division

slides = []
def slide(f, data=None, width=800, height=600):
	if data is None: data = {}
	#slides[:0] = [(f, data, width, height)]
	slides.append ((f, data, width, height))
	return f

import pango, pangocairo, cairo, os, signal

#
# Slides start here
#

def text_slide(title, text):
	def closure(r):
		r.move_to (20, 20)
		l = r.create_layout('')
		l.set_text(title)
		l.set_font_description (pango.FontDescription("roboto bold 48"))
		r.show_layout(l)
		r.move_to (20, 100)
		l.set_text(text.replace('\n', ' '))
		l.set_font_description (pango.FontDescription("roboto 24"))
		l.set_width (700 * pango.SCALE)
		r.show_layout(l)
		r.set_allocation(0,0,800,600)
	slide(closure)

if False:
	text_slide("descender alignment", """
	lolkasjd flkasjd
	flkajsd flkasjd flkajds
	flkasjd flkajsd flaksdj f
	""")

def showcase_slide(fonts, text, guides = [90, 60, 30, -30]):

	pageno = 1 + len(slides)

	def closure(r):
		r.move_to(400, 595)
		r.put_text(str(pageno), desc="roboto 20px", halign=0, valign=-1)

		width = None#800
		l = r.create_layout('')
		#tb = pango.TabArray (1, True)
		#tb.set_tab (0, pango.TAB_LEFT, 120)
		#l.set_tabs(tb)
		l.set_text(text)
		num = len(fonts)
		lsize = (600 - 2*20) / num
		for i,f in enumerate(fonts):

			size = lsize * .6
			l.set_font_description (pango.FontDescription(f + " %g"%size))
			ink,logical = l.get_extents()

			if width is None:
				width = logical[2]/pango.SCALE

			size *= width / (logical[2]/pango.SCALE)
			l.set_font_description (pango.FontDescription(f + " %g"%size))
			ink,logical = l.get_extents()

			x = (800 - width) / 2
			y = 20 + (i + .6) * lsize
			r.set_line_width (1)

			r.move_to (x - 30, y)
			r.line_to (x + width + 30, y)
			r.set_source_rgb (.6, .6, .6)
			r.stroke ()

			for g in guides:
				r.move_to (x - 30, y - g)
				r.line_to (x + width + 30, y - g)
				r.set_source_rgb (.8, .8, .8)
				r.stroke ()

			r.set_source_rgb (.2, .2, .2)
			r.move_to (x, y)
			r.show_layout_line(l.get_line(0))

		r.set_allocation(0,0,800,600)
	slide(closure)

sans = 'Arabic Sans BR'
naskh = 'Noto Naskh Arabic'
nazli = 'nazli'
mitra = 'bmitra'
roya = 'roya'
nassim = 'bbc nassim'

fonts = [sans, naskh, nazli, mitra]

showcase_slide(fonts, "ل ن س ی چ و ر")
showcase_slide(fonts, "‍ل ‍ن ‍س ‍ی ‍چ ‍و ‍ر")
showcase_slide(fonts, "ل ‍ل ن ‍ن ی ‍ی")
showcase_slide(fonts, "د ‍د ر ‍ر و ‍و")
showcase_slide(fonts, "ک ک‍ ‍ک ‍ک‍")
showcase_slide(fonts, "گ گ‍ ‍گ ‍گ‍")
showcase_slide(fonts, "چ چ‍ ‍چ ‍چ‍")
showcase_slide(fonts, "با یا پا")
showcase_slide(fonts, "م م‍ ‍م ‍م‍")
showcase_slide(fonts, "آ ا للل کگ")
showcase_slide(fonts, "گ ققق‌ق ففف‌ف")
showcase_slide(fonts, "۰۱۲۳۴۵۶۷۸۹")

fonts = [sans, naskh]

showcase_slide(fonts, "مالم‌مللم")
showcase_slide(fonts, "تواناتر")
showcase_slide(fonts, "سرافراز")
showcase_slide(fonts, "سیبپببر")
showcase_slide(fonts, "سیستم")
showcase_slide(fonts, "د ‍د ر ‍ر")

if __name__ == "__main__":

	import os
	import os.path
	fonts_conf = os.path.abspath(os.path.join (os.path.dirname(__file__), "fonts.conf"))
	os.putenv("FONTCONFIG_FILE", fonts_conf)

	import slippy
	import theme
	slippy.main (slides, theme)
