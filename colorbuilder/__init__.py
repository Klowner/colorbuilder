#!/usr/bin/env python
import re
import colorsys
import decimal

__version__ = '0.1'

class ColorFunc(object):
	MATCH = re.compile('^([a-z]+)\(([^\)]+)')
	def __init__(self, value):
		self.func_name, self.func_args = self.MATCH.match(value).groups()
		self.func_args = [x.strip() for x in filter(lambda x:x, self.func_args.split(','))]
	
	def __repr__(self):
		return "%s[%s]" % ( self.__class__.__name__, self.func_name )

	def resolve(self, parser, prop):
		funcname = "func_%s" % self.func_name
		func = getattr(self, funcname, None)
		if callable(func):
			return func(prop)
		else:
			raise ValueError

	def hsv_op(self, color_elem, prop, clamp=False):
		adjust = float( decimal.Decimal(self.func_args[0]) / decimal.Decimal('255') )
		elements = list(colorsys.rgb_to_hls(*prop))
		elements[color_elem] += adjust
		if clamp:
			elements[color_elem] = max(min(elements[color_elem], 1), 0)

		return colorsys.hls_to_rgb(*elements)

	def func_hue(self, prop):
		return self.hsv_op(0, prop)

	def func_brightness(self, prop):
		return self.hsv_op(1, prop, clamp=True)

	def func_saturation(self, prop):
		return self.hsv_op(2, prop, clamp=True)


class ColorName(object):
	MATCH = re.compile('^([A-Z0-9_]+)')
	def __init__(self, value):
		self.value = value.strip()

	def __repr__(self):
		return "%s[%s]" % ( self.__class__.__name__, self.value )

	def resolve(self, parser, prop):
		if prop:
			raise ValueError, 'ColorName does not accept operational values'
		if self.value not in parser.colors:
			raise ValueError, 'ColorName: %s not defined' % self.value

		return parser.get(self.value, as_tuple=True)
	

class ColorHex(object):
	MATCH = re.compile('^#([A-Fa-f|\d]{6})')
	def __init__(self, value):
		value = self.MATCH.match(value).groups()[0]
		self.value = (
			int(value[0:2], 16) / 255.0, # Red		
			int(value[2:4], 16) / 255.0, # Blue
			int(value[4:6], 16) / 255.0, # Green
			)
		
	def resolve(self, parser, prop):
		if prop:
			raise ValueError, 'ColorHex does not accept operational values'
		return self.value


class ColorsParser(object):
	STATEMENT_TYPES = [
		ColorFunc,
		ColorName,
		ColorHex,
	]

	def __init__(self, src=None):
		self.colors = {}
		if src:
			for row in src:
				self.add_item(row)

	def add_item(self, row):
		tokens = self._tokenize(row)
		if tokens:
			statements = self.parse_statements(tokens[1])	
			name = tokens[0]
		else:
			statements = None
		
		if statements:
			self.colors[name] = statements

	def _tokenize(self, row):
		if ':' in row:
			name, statement = row.split(':')[:2]
			statements = filter(lambda x:x, statement.split(' '))
			return (name, statements)
		return None

	def parse_statements(self, statements):
		results = []
		for stmt in statements:
			results.append( self._statement_get_type(stmt) )
		return results
			
	
	def _statement_get_type(self, statement):
		for SType in self.STATEMENT_TYPES:
			match = SType.MATCH.match(statement)
			if match:
				return SType(statement)
		return None

	def resolve(self, statements):
		left_prop = None
		for prop in statements:
			left_prop = prop.resolve(self, left_prop)
		return left_prop
	
	def to_hex(self, rgb):
		result = '#'
		for x in rgb:
			result += ("%02x" % int(round(x*255)))
		return result

	def get(self, name, as_tuple=False):
		result = self.resolve(self.colors[name])
		if as_tuple:
			return result
		return self.to_hex(result)

class TemplateProcessor(object):
	def __init__(self, color_parser):
		self.color_parser = color_parser

	def process(self, source):
		tokens = self._tokenize(source)
		cp = self.color_parser
		out = []
		for (is_statement, token) in tokens:
			if is_statement:
				stmt_result = cp.to_hex(cp.resolve(cp.parse_statements( token )))
				out.append( stmt_result)
			else:
				out.append( token )
		return out	

	def _tokenize(self, istream):
		import StringIO
		results = []
		obuff = StringIO.StringIO()
		mode = 0		

		while True:
			c = istream.read(1)
			if mode == 0:
				if c == '$':
					if istream.read(1) == '[':
						obuff.seek(0)
						results.append((mode, obuff.read()))
						obuff.truncate(0)
						mode = 1
					else:
						istream.seek(istream.tell()-1)		
						obuff.write(c)
				else:
					obuff.write(c)
			else:
				if c == ']':
					obuff.seek(0)
					results.append((mode, obuff.read().split(' ')))
					obuff.truncate(0)
					mode = 0
				else:
					obuff.write(c)
			
			if not c:
				break
		
		obuff.seek(0)
		results.append((mode, obuff.read()))
		return results


def main():
	import argparse
	import sys

	parser = argparse.ArgumentParser(description='Process color definition file(s) and spew out a useful result.')
	parser.add_argument('template', nargs=1, type=argparse.FileType('r'))
	parser.add_argument('colordefs', nargs='+', type=argparse.FileType('r'))
	parser.add_argument('-o', dest='output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
	
	args = parser.parse_args()
	
	color_parser = ColorsParser()
	for colordef in args.colordefs:
		[color_parser.add_item(x) for x in colordef.readlines()]

	
	template = TemplateProcessor(color_parser)	
	results = template.process(args.template[0])
	
	args.output.write(''.join(results))


if __name__ == '__main__':
	main()
