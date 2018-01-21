# vim: set fileencoding=utf-8 :
# Written by Behdad Esfahbod, 2014
# Not copyrighted, in public domain.

# A theme file should define two functions:
#
# - prepare_page(renderer): should draw any background and return a tuple of
#   x,y,w,h that is the area to use for slide canvas.
# 
# - draw_bubble(renderer, x, y, w, h, data=None): should setup canvas for the
#   slide to run.  Can draw a speaking-bubble for example.  x,y,w,h is the
#   actual extents that the slide will consume.  Data will be the user-data
#   dictionary from the slide.
#
# Renderer is an object similar to a cairo.Context and pangocairo.CairoContext
# but has its own methods too.  The more useful of them here are put_text and
# put_image.  See their pydocs.

def prepare_page (renderer):
	cr = renderer.cr
	cr.set_source_rgb (1, 1, 1)
	cr.paint ()
	cr.set_source_rgb (0, 0, 0)
	return 0, 0, renderer.width, renderer.height

def draw_bubble (renderer, x, y, w, h, data={}):
	pass
