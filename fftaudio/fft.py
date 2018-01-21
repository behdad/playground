#!/usr/bin/python3

import numpy as np
import math

f = open('/dev/stdin', 'rb')

freq = 44100
time = .1
cutoff_freq = (1./time) * 2 * 4

i = 0
while True:
	signal = list(f.read(int(freq * time)))
	n = len(signal)
	fft = abs(np.fft.fft(signal)[:n/2] / (n / 2.))

	# high-pass filtering.
	fft[:1+(cutoff_freq * time)] = 0

	# log-scale and quantize; throws away noise.
	fft = np.floor(np.log(1+fft))

	# skip silence.
	if np.all(fft == 0):
		continue

	note_freq = int(fft.argmax() / time)
	note = round(math.log(note_freq / 440., 2**(1/12.)))
	octave = 4 + int(note / 12)
	note = note % 12
	note = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#'][note]
	note += str(octave)

	print(note, '%4d'%note_freq, ''.join('%1X' % x for x in fft[:200]))
