#!/usr/bin/env python

import colorsys

def hex2rgb(x):
	x.strip('#')
	r = int(x[0:2],16) / 255.
	g = int(x[2:4],16) / 255;
	b = int(x[4:6],16) / 255;
	return (r,g,b)

def colordiff(a,b):
	a_rgb = hex2rgb(a)
	b_rgb = hex2rgb(b)
	
	a_hls = colorsys.rgb_to_hls(*a_rgb)
	b_hls = colorsys.rgb_to_hls(*b_rgb)

	result = {}
	for x,k in enumerate('hls'):
		result[k] = b_hls[x] - a_hls[x]
		print k.upper(), ': ', round(result[k],2),'\t', int(round(result[k]*255))

	funcs = {
		'h':'hue',
		's':'saturation',
		'l':'brightness',
	}

	statement = '#%s ' % a
	for k,v in result.items():
		if v != 0:
			print v
			statement += "%s(%s) " % (funcs[k], int(round(result[k]*255,1)))
	print statement
						
	
