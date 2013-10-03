#!/usr/bin/python

from allchars10 import charstrings
import itertools
import time
import sys
import heapq

class String (object):

	def __init__ (self, iterable):
		self.value = tuple (iterable)

	def __len__ (self):
		return len (self.value)

	def __getitem__ (self, i):
		return self.value[i]

	def __iter__ (self):
		return iter (self.value)

	def __str__ (self):
		return str (self.value)

	def __repr__ (self):
		return "%s(%s)" % (self.__class__.__name__, str (self))

	def __cmp__ (self, other):
		return cmp (self.value, other.value)


class Suffix (object):

	def __init__ (self, item, index):
		self.item = item
		self.index = index

	@property
	def value (self):
		return self.item[self.index:]

	def __len__ (self):
		return len (self.item) - index

	def __getitem__ (self, i):
		if isinstance (i, slice):
			indices = xrange (*i.indices (len (self)))
			return [self[i] for i in indices]
		return self.item[self.index + i]

	def __iter__ (self):
		return itertools.islice (self.item, self.index, None)

	def __str__ (self):
		return str (self.value)

	def __repr__ (self):
		return "%s(%d, %d)" % (self.__class__.__name__, self.item, self.index)

	def __cmp__ (self, other):
		return cmp (self.value, other.value)

charstrings = [String(s) for s in charstrings]

start_time = time.time ()

def find_suffixes (strings):
	"""Return list of all suffixes of strings."""
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


class Substring (object):

	def __init__ (self, item, start, end, freq):
		self.item = item
		self.start = start
		self.end = end
		self.freq = freq

	@property
	def value (self):
		return self.item[self.start:self.end]

	def __len__ (self):
		return end - start

	def __getitem__ (self, i):
		if isinstance (i, slice):
			indices = xrange (*i.indices (len (self)))
			return [self[i] for i in indices]
		if i >= self.end - self.start:
			raise IndexError ()
		return self.item[self.start + i]

	def __iter__ (self):
		return itertools.islice (self.item, self.start, self.end)

	def __str__ (self):
		return str (self.value)

	def __repr__ (self):
		return "%s(%d, %d, %d)" % (self.__class__.__name__, self.item,
					   self.start, self.end, self.freq)

	def __cmp__ (self, other):
		return cmp (self.value, other.value)

	def cost (self):
		return len (self) # XXX Return byte cost

	def subr_saving (self, call_cost = 2, subr_overhead = 2):
		return (self.cost () * self.freq   # Avoided copies
		        - self.cost ()             # Subroutine body
		        - call_cost * self.freq    # Cost of calling
		        - subr_overhead            # Overhead of defining subroutine
		       )


def find_substrings (suffixes, min_freq = 2):
	"""Return all substrings of suffixes with frequency >= min_freq."""

	substrs = []
	start_indices = []
	previous = []
	previous_s = None
	for i,s in enumerate (suffixes):
		current = s.value

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
