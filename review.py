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

def group2(iterable):
	it = iter(iterable)
	while True:
		yield next(it),next(it)

def filter_path_keep_counters(r):
	path = r.copy_path()
	lpath = list(path)
	# Calc total area, so we know font winding direction
	area = 0
	for op,coords in lpath:
		if op == 0: # moveto
			lx,ly = coords
			continue
		for x,y in group2(coords):
			area += (x-lx) * (y+ly) / 2.
			lx,ly = x,y
	total_area = area

	# Record counters
	all_ops = []
	all_coords = []
	for i,(op,coords) in enumerate(lpath):
		if op == 0: # moveto
			mx,my = coords
			lx,ly = mx,my
			area = 0
			start = i
			continue
		for x,y in group2(coords):
			area += (x-lx) * (y+ly) / 2.
			lx,ly = x,y
		if op == 3: # closepath
			x,y = mx,my
			area += (x-lx) * (y+ly) / 2.
			if (area < 0) != (total_area < 0):
				for vop,vcoords in lpath[start:i+1]:
					all_ops.append(vop)
					all_coords.extend(vcoords)

	# Reverse contours
	new_ops = []
	new_coords = []
	points = reversed(list(group2(all_coords)))
	for op in reversed(all_ops):
		if op == 0: # moveto
			op = 3 # closepath
			args = 1
		elif op == 1: # lineto
			args = 1
		elif op == 2: # curveto
			args = 3
		elif op == 3: # closepath
			op = 0 # move_to
			args = 0

		new_ops.append(op)
		for i in range(args):
			p = next(points)
			new_coords.extend(p)

	r.new_path()

	it = iter(new_coords)
	for op in new_ops:
		func,nargs = {
		0: ('move_to', 1),
		1: ('line_to', 1),
		2: ('curve_to', 3),
		3: ('close_path', 0),
		}[op]

		args = []
		for i in range(2*nargs):
			args.append(next(it))

		getattr(r, func)(*args)
	#r.append_path(path)

def showcase_slide(fonts, texts,
		   guides = [90, 60, 30, -30],
		   direction=None,
		   fill=.4,
		   stroke=.8,
		   counters=False):

	pageno = 1 + len(slides)
	if type(fonts) not in [list, tuple]: fonts = [fonts]
	if type(texts) not in [list, tuple]: texts = [texts]

	def closure(r):
		r.move_to(400, 595)
		r.put_text(str(pageno), desc="roboto 20px", halign=0, valign=-1)

		width = None#800
		l = r.create_layout('')
		tb = pango.TabArray (1, True)
		ntabs = len([x for x in texts[0] if x == '\t'])
		tb.set_tab (0, pango.TAB_LEFT, int(700 / (1 + ntabs)))
		l.set_tabs(tb)
		if direction is not None:
			l.set_auto_dir(False)
			l.get_context().set_base_dir(direction)

		font_size = {}
		for it,text in enumerate(texts):
			l.set_text(text)
			num = len(fonts)
			lsize = (600 - 2*20) / num
			for i,f in enumerate(fonts):

				size = lsize * .6
				l.set_font_description (pango.FontDescription(f + " %g"%size))
				ink,logical = l.get_extents()

				if width is None:
					width = logical[2]/pango.SCALE

				if f not in font_size:
					size *= width / (logical[2]/pango.SCALE)
					font_size[f] = size
				else:
					size = font_size[f]
				l.set_font_description (pango.FontDescription(f + " %g"%size))
				ink,logical = l.get_extents()

				if direction is None:
					x = (800 - width) / 2
				else:
					if direction == pango.DIRECTION_LTR:
						x = 50
					else:
						x = 750 - width

				y = 20 + (i + .6) * lsize
				r.set_line_width (1)

				if it == 0 and guides is not None:
					r.move_to (x - 30, y)
					r.line_to (x + width + 30, y)
					r.set_source_rgb (.6, .6, .6)
					r.stroke ()

					for g in guides:
						r.move_to (x - 30, y - g)
						r.line_to (x + width + 30, y - g)
						r.set_source_rgb (.8, .8, .8)
						r.stroke ()

				color = {
				1: [(0,0,0)],
				2: [(1,0,0),(0,0,1)],
				3: [(1,0,0),(0,0,1),(0,1,0)],
				}[len(texts)][it]

				if fill:
					r.move_to (x, y)
					r.set_source_rgba (color[0],color[1],color[2],float(fill))
					#r.show_layout_line(l.get_line(0))
					r.layout_line_path(l.get_line(0))
					r.fill()
				if stroke:
					r.move_to (x, y)
					r.layout_line_path(l.get_line(0))
					r.set_source_rgba (color[0],color[1],color[2],float(stroke))
					r.stroke()
				if counters:
					r.move_to (x, y)
					r.layout_line_path(l.get_line(0))
					filter_path_keep_counters(r)
					r.set_source_rgba (1,0,0,float(counters))
					r.fill()

		r.set_allocation(0,0,800,600)
	slide(closure)

sans = 'Arabic Sans BR'
naskh = 'Noto Naskh Arabic'
nazli = 'nazli'
mitra = 'bmitra'
roya = 'roya'
nassim = 'bbc nassim'

fonts = [sans, naskh, nazli, mitra]

showcase_slide(fonts, "ل ن س ی چ غ ور")
showcase_slide(fonts, "‍ل ‍ن ‍س ‍ی ‍چ ‍غ ‍و‍ر")
showcase_slide(fonts, ["‍ل	‍ن	‍ی", "ل	ن	ی"], direction=pango.DIRECTION_LTR)
showcase_slide(fonts, "د ‍د ر ‍ر و ‍و")
showcase_slide(fonts, "ذ ‍ذ ز ‍ز ژ ‍ژ")
showcase_slide(fonts, "ک ک‍ ‍ک ‍ک‍")
showcase_slide(fonts, "گ گ‍ ‍گ ‍گ‍")
showcase_slide(fonts, "ح ح‍ ‍ح ‍ح‍")
showcase_slide(fonts, "ج ج‍ ‍ج ‍ج‍")
showcase_slide(fonts, "خ خ‍ ‍خ ‍خ‍")
showcase_slide(fonts, "چ چ‍ ‍چ ‍چ‍")
showcase_slide(fonts, "‍و و‍ چ‍ ‍چ ‍چ‍")

showcase_slide(fonts, "غ غ‍ ‍غ ‍غ‍")

fonts = [sans, naskh]
showcase_slide(fonts, "‍غ ‍غ‍", counters=True)
showcase_slide(fonts, "‍غ ‍غ‍", counters=True, fill=False, stroke=False, guides=None)
fonts = [sans, naskh, nazli, mitra]

showcase_slide(fonts, "ه ه‍ ‍ه ‍ه‍")
showcase_slide(fonts, "با یا پا")
showcase_slide(fonts, "لا ‍لا")
showcase_slide(fonts, "ی ‍ی")
showcase_slide(fonts, "م م‍ ‍م ‍م‍")
showcase_slide(fonts, "م م‍ ‍م ‍م‍", counters=True)
showcase_slide(fonts, "م م‍ ‍م ‍م‍", counters=True, fill=False, stroke=False, guides=None)
showcase_slide(fonts, "آ ا لا  للل کگ")
showcase_slide(fonts, "ققق‌ق ففف‌ف")
showcase_slide(fonts, "ققق‌ق ففف‌ف", counters=True)
showcase_slide(fonts, "ققق‌ق ففف‌ف", counters=True, fill=False, stroke=False, guides=None)
showcase_slide(fonts, "۰۱۲۳۴۵۶۷۸۹")
showcase_slide(fonts, "سلام، برو.")
showcase_slide(fonts, "چ	چ‍", direction=pango.DIRECTION_LTR)
showcase_slide(fonts, "‍چ	‍چ‍", direction=pango.DIRECTION_LTR)
showcase_slide(fonts, ["‍چ	‍چ‍","چ	چ‍"], direction=pango.DIRECTION_LTR)
for f in fonts:
	showcase_slide(f, ["‍چ	‍چ‍", "چ	چ‍"], direction=pango.DIRECTION_LTR)

fonts = [sans, naskh]

showcase_slide(fonts, "مالم‌مللم")
showcase_slide(fonts, "تواناتر")
showcase_slide(fonts, "سرافراز")
showcase_slide(fonts, "سیبپببر")
showcase_slide(fonts, "سیستم")
showcase_slide(fonts, "‍دد ‍رر ‍وو")
showcase_slide(fonts, "د	ر	و", direction=pango.DIRECTION_LTR)
showcase_slide(fonts, "‍د	‍ر	‍و", direction=pango.DIRECTION_LTR)
for f in fonts:
	showcase_slide(f, ["‍د	‍ر	‍و", "د	ر	و"], direction=pango.DIRECTION_LTR)

if __name__ == "__main__":

	import os
	import os.path
	fonts_conf = os.path.abspath(os.path.join (os.path.dirname(__file__), "fonts.conf"))
	os.putenv("FONTCONFIG_FILE", fonts_conf)

	import slippy
	import theme
	slippy.main (slides, theme)
