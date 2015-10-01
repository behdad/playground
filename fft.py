#!/usr/bin/python3

import numpy as np

f = open('/dev/stdin', 'rb')

freq = 44100
time = .08

i = 0
while True:
	signal = list(f.read(int(freq * time)))
	n = len(signal)
	fft = abs(np.fft.fft(signal)[1:n/2] / (n / 2.))
	note = fft.argmax() / time

	print(note, '	', sep='', end='')
	i += 1
	if i % 8 == 0:
		print()
