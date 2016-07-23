#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import
import sys
import array
import collections
from gi.repository import HarfBuzz as hb
from gi.repository import GLib

# Python 2/3 compatibility
try:
	unicode
except NameError:
	unicode = str

def tounicode(s, encoding='utf-8'):
	return s if isinstance(s, unicode) else s.decode(encoding)
def tobytes(s, encoding='utf-8'):
	return s if isinstance(s, bytes) else s.encode(encoding)


def harfbuzz_open_font(fontpath):
	"""Open font and return HarfBuzz font object."""
	# Need to create GLib.Bytes explicitly until this bug is fixed:
	# https://bugzilla.gnome.org/show_bug.cgi?id=729541
	fontdata = open (fontpath, 'rb').read ()
	blob = hb.glib_blob_create (GLib.Bytes.new (fontdata))
	face = hb.face_create (blob, 0)
	del blob
	font = hb.font_create (face)
	scale = 1000 # hb.face_get_upem (face)
	del face
	hb.font_set_scale (font, scale, scale)
	hb.ot_font_set_funcs (font)
	return font

def harfbuzz_width(lines, hb_font):
	"""Return list of widths for strings in lines, when
	rendered with HarfBuzz using hb_font.  Return value is in
	thousandth of EM (ie. font-size=1000)."""
	out = []
	buf = hb.buffer_create ()
	for text in lines:
		hb.buffer_clear_contents (buf)
		hb.buffer_add_utf8 (buf, tobytes(text), 0, -1)
		hb.buffer_guess_segment_properties (buf)

		hb.shape (hb_font, buf, [])

		positions = hb.buffer_get_glyph_positions (buf)
		w = sum(pos.x_advance for pos in positions)
		out.append(w)
	return out

def browser_width(lines, W):
	"""Return list of widths for strings in lines, using
	W to lookup the width of each Unicode codepoint.  W
	should support __getitem__ mapping from integer to
	integer."""
	out = []
	for text in lines:
		w = 0
		for c in text:
			w += W[ord(c)]
		out.append(w)
	return out

BrowserWidth = collections.Counter

def nominal_browserwidth(charset, hb_font):
	"""Returns width-vector for characters in charset
	representing their nominal width in hb_font."""

	W = BrowserWidth() # Just to get default=0

	for u in sorted(charset):
		found, gid = hb.font_get_nominal_glyph(hb_font, u)
		if not found:
			print("Warning, font does not cover U+%04X" % u)
		W[u] = hb.font_get_glyph_h_advance(hb_font, gid)
	return W


def regression_browserwidth(charset,
			    training_data,
			    training_expected,
			    start_width=None,
			    tolerance=2e-3,
			    iterations=100,
			    verbose=False):
	"""Train and return a browserwidth vector based on training_data
	and training_expected.  If a reasonable start_width is provided,
	it will speed up training."""

	import numpy as np
	from scipy.sparse import dok_matrix
	from scipy.sparse.linalg import lsqr

	mapping = sorted(charset)
	reverse = {v:i for i,v in enumerate(mapping)}

	A = dok_matrix((len(training_data), len(mapping)), dtype=np.int32)
	for i,text in enumerate(training_data):
		d = collections.Counter()
		for c in text:
			d[c] += 1
		for k,v in d.items():
			A[i,reverse[ord(k)]] = v

	b = np.array(training_expected)
	if start_width:
		b -= np.array(browser_width(training_data, start_width))

	x,_,n,e2 = lsqr(A,b,
			atol=tolerance,btol=tolerance,iter_lim=iterations,
			show=verbose)[:4]

	W = BrowserWidth()
	for i,v in enumerate(x):
		W[mapping[i]] = v
	if start_width:
		for u in charset:
			W[u] += start_width[u]

	return W

def print_error_metrics(expected, actual, description=None):
	"""Print error statistics for actual, given expected."""

	import statistics

	print()
	if description:
		print("Error report for %s:" % description)

	residual = [e-a for e,a in zip(expected,actual)]
	mean = statistics.mean(residual)
	stddev = statistics.pstdev(residual, mean)

	print("error mean=%0.3fem stddev=%0.3fem" %
	      (.001*mean, .001*stddev))

	residual = [abs(e-a)/e for e,a in zip(expected,actual) if e]
	mean = statistics.mean(residual)
	stddev = statistics.pstdev(residual, mean)
	print("abs-error mean=%4.1f%% stddev=%4.1f%%" %
	      (100*mean, 100*stddev))

	print()

def open_text(textfile):
	if textfile.endswith('.bz2'):
		import bz2
		Open = bz2.BZ2File
	else:
		Open = open
	with Open(textfile) as f:
		while True:
			yield tounicode(f.readline().strip())

def main(fontfile, textfile, verbose=False):

	# TODO: integrate word frequencies.

	hb_font = harfbuzz_open_font(sys.argv[1])
	text = iter(open_text(textfile))

	N = 10000
	training_data = []
	test_data = []
	for i in range(N):
		line = next(text)
		if i % 10 == 0:
			test_data.append(line)
		else:
			training_data.append(line)

	training_expected = harfbuzz_width(training_data, hb_font)
	test_expected = harfbuzz_width(test_data, hb_font)

	charset = set()
	for line in training_data: charset.update(ord(x) for x in line)
	for line in test_data:     charset.update(ord(x) for x in line)

	W = nominal_browserwidth(charset, hb_font)
	test_actual = browser_width(test_data, W)
	print_error_metrics(test_expected, test_actual, description='nominal')

	W2 = regression_browserwidth (charset,
				      training_data,
				      training_expected,
				      start_width=W,
				      verbose=verbose)
	test_actual = browser_width(test_data, W2)
	print_error_metrics(test_expected, test_actual, description='regression')


if __name__ == '__main__':
	verbose = False
	if sys.argv[1] == '--verbose':
		verbose = True
		del sys.argv[1]
	fontfile = sys.argv[1]
	textfile = sys.argv[2]
	main(fontfile, textfile, verbose=verbose)
