#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import
import sys
import array
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

fontdata = open (sys.argv[1], 'rb').read ()
textfile = sys.argv[2]

N = 10000
training_data = []
test_data = []
with open(textfile) as f:
	for i in range(N):
		line = tounicode(f.readline().strip())
		if i % 10 == 0:
			test_data.append(line)
		else:
			training_data.append(line)

# Need to create GLib.Bytes explicitly until this bug is fixed:
# https://bugzilla.gnome.org/show_bug.cgi?id=729541
blob = hb.glib_blob_create (GLib.Bytes.new (fontdata))
face = hb.face_create (blob, 0)
del blob
font = hb.font_create (face)
upem = hb.face_get_upem (face)
del face
hb.font_set_scale (font, upem, upem)
hb.ot_font_set_funcs (font)
buf = hb.buffer_create ()

def expected_width(lines):
	out = []
	for text in lines:
		hb.buffer_clear_contents (buf)
		hb.buffer_add_utf8 (buf, tobytes(text), 0, -1)
		hb.buffer_guess_segment_properties (buf)

		hb.shape (font, buf, [])

		positions = hb.buffer_get_glyph_positions (buf)
		w = sum(pos.x_advance for pos in positions)
		out.append(w)
	return out

def browser_width(lines, W):
	out = []
	for text in lines:
		w = 0
		for c in text:
			w += W[c]
		out.append(w)
	return out


training_expected = expected_width(training_data)
test_expected = expected_width(test_data)

chars = set()
for line in training_data: chars.update(line)
for line in test_data:     chars.update(line)

W = {}
for c in sorted(chars):
	found, gid = hb.font_get_nominal_glyph(font, ord(c))
	if not found:
		print("Warning, font does not cover U+%04X" % ord(c))
	W[c] = hb.font_get_glyph_h_advance(font, gid)


test_actual = browser_width(test_data, W)
print(sum(test_expected))
print(sum(test_actual))
err = []
for e,a in zip(test_expected, test_actual):
	err.append(abs(a-e) / e)
print(100. * sum(err) / len(err))

import numpy as np
from scipy.sparse import dok_matrix
from scipy.sparse.linalg import spsolve, lsqr

A = dok_matrix((len(training_data), 1+max(ord(c) for c in chars)), dtype=np.int32)
for i,text in enumerate(training_data):
	d = {}
	for c in text:
		d[c] = d.get(c, 0) + 1
	for k,v in d.items():
		A[i,ord(k)] = v

b = np.array(training_expected)
print (A.shape, b.shape)
X = lsqr(A, b)

W2 = {}
for i,w in enumerate(list(X[0])):
	W2[unichr(i)] = w

test_actual = browser_width(test_data, W2)
print(sum(test_actual))
err = []
for e,a in zip(test_expected, test_actual):
	err.append(abs(a-e) / e)
print(100. * sum(err) / len(err))
