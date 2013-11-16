#!/usr/bin/python

from allchars1000 import charstrings
import itertools
import time
import sys
import heapq

_interned_strings = {}
def intern_string  (iterable):
	k = tuple (iterable)
	v = _interned_strings.get (k, None)
	if v is None:
		_interned_strings[k] = k
		v = k
	return v


class String (object):

	def __init__ (self, iterable):
		self.value = intern_string (iterable)

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

	def suffix (self, start = 0):
		return Suffix (self.value, start)


class Suffix (String):

	def __init__ (self, item, start = 0):
		self.__item = intern_string (item)
		self.__start = start
		self.__value = self.__item[self.__start:]

	@property
	def value (self):
		return self.__item[self.__start:]

	def __len__ (self):
		return len (self.__item) - self.__start

	def __getitem__ (self, i):
		if isinstance (i, slice):
			indices = xrange (*i.indices (len (self)))
			return [self[i] for i in indices]
		return self.__item[self.__start + i]

	def __iter__ (self):
		return itertools.islice (self.__item, self.__start, None)

	def prefix (self, end, freq):
		assert self.__start + end <= len (self.__item)
		return Substring (self.__item, self.__start, self.__start + end, freq)


def find_suffixes (strings):
	"""Return list of all suffixes of strings."""
	suffixes = []
	for item in strings:
		for start in range (len (item)):
			suffixes.append (item.suffix (start))
	return suffixes


class Substring (String):

	def __init__ (self, item, start = 0, end = -1, freq = 1):
		self.__item = intern_string (item)
		self.__start = start
		self.__end = end
		self.__freq = freq
		self.__value = self.__item[self.__start:self.__end]

	@property
	def value (self):
		return self.__item[self.__start:self.__end]

	def __len__ (self):
		return self.__end - self.__start

	def __getitem__ (self, i):
		if isinstance (i, slice):
			indices = xrange (*i.indices (len (self)))
			return [self[i] for i in indices]
		if i >= self.__end - self.__start:
			raise IndexError ()
		return self.__item[self.__start + i]

	def __iter__ (self):
		return itertools.islice (self.__item, self.__start, self.__end)

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
			substr = previous_s.prefix (l + 1, freq)
			substrs.append (substr)

		previous = current
		previous_s = s
		start_indices = start_indices[:min_l]
		start_indices += [i] * (len (current) - min_l)
	
	return substrs


charstrings = [String(s) for s in charstrings]
start_time = time.time ()
suffixes = find_suffixes (charstrings)
print "Built suffixes: %d" % len (suffixes)
print "time ", time.time () - start_time; start_time = time.time ()
suffixes.sort ()
print "Sorted suffixes"
print "time ", time.time () - start_time; start_time = time.time ()
substrs = find_substrings (suffixes)
print "Found substrings: %d" % len (substrs)
print "time ", time.time () - start_time; start_time = time.time ()
heap = heapq.heapify (substrs)
print "Heapified substrings"
print "time ", time.time () - start_time; start_time = time.time ()
