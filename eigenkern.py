#!/usr/bin/python

from fontTools.ttLib import TTFont
import numpy as np
import scipy.sparse.linalg
import scipy.cluster.vq

def load_pairpos(lookup, font):
	print "Loading pairpos lookup"
	glyphIDs = font.getReverseGlyphMap()
	n = len(glyphIDs)

	# Load kern matrix
	f1 = 0
	f2 = 0
	matrix = np.zeros((n,n))
	for st in reversed(lookup.SubTable):
		print "Loading subtable format", st.Format
		assert st.ValueFormat1 is 4
		assert st.ValueFormat2 is 0 # TODO handle RTL
		leftGlyphs = st.Coverage.glyphs
		if st.Format is 1:
			for left,pairs in zip(leftGlyphs, st.PairSet):
				left = glyphIDs[left]
				for pair in pairs.PairValueRecord:
					right = glyphIDs[pair.SecondGlyph]
					kern = pair.Value1.XAdvance
					matrix[left,right] = kern
					f1 += 1
		elif st.Format is 2:
			print "Class1 count %d, class2 count %d" % (st.Class1Count, st.Class2Count)
			for left,class1 in st.ClassDef1.classDefs.items():
				left = glyphIDs[left]
				row = st.Class1Record[class1]
				for right,class2 in st.ClassDef2.classDefs.items():
					right = glyphIDs[right]
					kern = row.Class2Record[class2].Value1.XAdvance
					matrix[left,right] = kern
					f2 += 1
		else:
			assert 0

	print "Loaded %d exceptions and %d class kerns" % (f1, f2)
	return matrix

def cluster(mat, k):
	centroids,labels = scipy.cluster.vq.kmeans2(mat, k)
	for i in range(len(mat)):
		mat[i,:] = centroids[labels[i],:]
	return mat

def optimize_pairpos(lookups, font):
	global matrix,u,s,v,appr,diff,u2,s2,v2,u2norm,v2norm

	glyphIDs = font.getReverseGlyphMap()
	n = len(glyphIDs)
	matrix = np.zeros((n,n))

	for lookup in lookups:
		submatrix = load_pairpos(lookup, font)
		matrix += submatrix

	k = 100
	tolerance = 100

	#u,s,v = np.linalg.svd(matrix)
	u,s,v = scipy.sparse.linalg.svds(scipy.sparse.csc_matrix(matrix), k=k)

	appr = np.matrix(u)*np.diag(s)*np.matrix(v)
	diff = matrix-appr
	print "Intolerant kerns", sum(sum(abs(np.asarray(diff))>tolerance))
	print "Max error", abs(diff).max()
	print "Sum error", abs(diff).sum()

	kk = 100
	u2 = cluster(scipy.cluster.vq.whiten(u), k=kk)
	v2 = cluster(scipy.cluster.vq.whiten(v.transpose()), k=kk).transpose()
	u2norm = u2.transpose().dot(u2).diagonal()
	v2norm = v2.dot(v2.transpose()).diagonal()
	s2 = s / u2norm / v2norm

	appr = np.matrix(u2)*np.diag(s2)*np.matrix(v2)
	diff = matrix-appr
	print "Intolerant kerns", sum(sum(abs(np.asarray(diff))>tolerance))
	print "Max error", abs(diff).max()
	print "Sum error", abs(diff).sum()

	return matrix

font = TTFont("Ubuntu-Regular.ttf")
gpos = font['GPOS'].table
lookups = [l for l in gpos.LookupList.Lookup if l.LookupType is 2]

optimize_pairpos(lookups, font)

#font.save("Roboto-Regular.ttf.eigen")
