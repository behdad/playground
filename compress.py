#!/usr/bin/python

from allchars10 import charstrings
import itertools
import time
import sys
import heapq

class Suffix:

	def __init__ (self, item, index):
		self.item = item
		self.index = index

	def suffix (self):
		return self.item[self.index:]

	def isuffix (self):
		return itertools.islice (self.item, self.index, None)

	def __str__ (self):
		return str (self.suffix ())

	def __cmp__ (self, other):
		for a,b in itertools.izip_longest (self.isuffix (), other.isuffix (), fillvalue=None):
			c = cmp (a, b)
			if c:
				return c
		return 0

start_time = time.time ()

# Build Suffix Array

def find_suffixes (strings):
	suffixes = []
	for item in strings:
		for index in range (len (item)):
			suffixes.append (Suffix (item, index))
	return suffixes

suffixes = find_suffixes (charstrings)

print "Built suffixes"
print "time ", time.time () - start_time; start_time = time.time ()

print len (suffixes)

suffixes.sort ()

print "Sorted suffixes"
print "time ", time.time () - start_time; start_time = time.time ()

# Build all substrings with frequency >= min_freq

class Substring:

	def __init__ (self, item, start, end, freq):
		self.item = item
		self.start = start
		self.end = end
		self.freq = freq

	def substring (self):
		return self.item[self.start:self.end]

	def isubstring (self):
		return itertools.islice (self.item, self.start, self.end)

	def __len__ (self):
		return self.end - self.start

	def __str__ (self):
		return str (self.substring ())

	def __cmp__ (self, other):
		for a,b in itertools.izip_longest (self.isubstring (), other.isubstring (), fillvalue=None):
			c = cmp (a, b)
			if c:
				return c
		return 0

	def cost (self):
		return len (self) * self.freq # XXX Return byte cost

	def subr_saving (self, call_cost = 2, subr_overhead = 2):
		return (self.cost ()               # Avoided copies
		        - len (self)               # Subroutine body
		        - call_cost * self.freq    # Cost of calling
		        - subr_overhead            # Overhead of defining subroutine
		       )


def find_substrings (suffixes, min_freq = 2):
	substrs = []
	start_indices = []
	previous = []
	previous_s = None
	for i,s in enumerate (suffixes):
		current = s.suffix ()

		if current == previous:
			continue

		max_l = min (len (previous), len (current))
		min_l = max_l
		for l in range (max_l):
			if previous[l] != current[l]:
				min_l = l
				break

		# First min_l items are still the same.

		# Pop the rest from previous and account for.
		for l in range (min_l, len (previous)):
			freq = i - start_indices[l]
			if freq < min_freq:
				break
			#if l + 1 < len (previous) and freq == i - start_indices[l+1]:
			#	continue
			substr = Substring (previous_s.item, previous_s.index,
					    previous_s.index + l + 1,
					    freq)
			substrs.append (substr)

		previous = current
		previous_s = s
		start_indices = start_indices[:min_l]
		start_indices += [i] * (len (current) - min_l)
	
	return substrs


substrs = heapq.heapify (find_substrings (suffixes))
