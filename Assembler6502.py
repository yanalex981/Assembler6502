import re
# import itertools

class TokenMatcher:
	def __init__(self, label, regex):
		self.label = label
		self.__regex = re.compile(regex)

	def __call__(self, string, pos=0):
		return self.__regex.match(string, pos)

	def __str__(self):
		return self.label

	__repr__ = __str__

mnemonic = {'ldx', 'lsr', 'rti', 'sta', 'bcs', 'brk', 'sed', 'sec', 'beq', 'cpy', 'pla', 'and', 'tax', 'sty', 'dey', 'inx', 'rts', 'sei', 'bne', 'bvc', 'eor', 'asl', 'cmp', 'txs', 'txa', 'jmp', 'ror', 'nop', 'stx', 'inc', 'iny', 'bvs', 'adc', 'cld', 'pha', 'tya', 'ora', 'plp', 'jsr', 'bit', 'lda', 'bmi', 'tsx', 'rol', 'cpx', 'php', 'dex', 'bpl', 'clv', 'clc', 'dec', 'bcc', 'ldy', 'tay', 'sbc', 'cli'}
instRegex = ''
for m in mnemonic:
	instRegex += '{}|'.format(m)
instRegex += instRegex.upper()
instRegex = '\\b({})\\b'.format(instRegex[:-1])

MNE    = TokenMatcher('Mnemonic'     , instRegex)
DEFINE = TokenMatcher('Define'       , r'\bdefine\b')
ID     = TokenMatcher('Identifier'   , r'[_a-zA-Z][_a-zA-Z0-9]*')
CONST  = TokenMatcher('Constant'     , r'(\d+|\$[0-9a-fA-F]+)\b')
SPACE  = TokenMatcher('Space'        , r'[ \t]+')
COLON  = TokenMatcher('Colon'        , r':')
HASH   = TokenMatcher('Hash'         , r'#')
LB     = TokenMatcher('Left bracket' , r'\(')
RB     = TokenMatcher('Right bracket', r'\)')
XI     = TokenMatcher('X index'      , r',\s*[Xx]\b')
YI     = TokenMatcher('Y index'      , r',\s*[Yy]\b')
EOL    = TokenMatcher('Newline'      , r'\r\n|\r|\n')

priorities = [EOL, MNE, DEFINE, ID, SPACE, HASH, CONST, XI, YI, COLON, LB, RB]

UNARY = 'Unary'
X_INDEX = 'X indexed'
Y_INDEX = 'Y indexed'

NULL = 'No param'
IMED = 'Immediate'
ABSL = 'Absolute'
REL = 'Relative'
INDR = 'Indirect'
ZPG  = 'Zero Page'
ZPGX = 'Zero Page X'
ZPGY = 'Zero Page Y'
XIND = 'X Indirect'
INDY = 'Indirect Y'
ABSX = 'Absolute X'
ABSY = 'Absolute Y'

opcodes = {
	('brk', NULL): 0x00, ('ora', XIND): 0x01,                                           ('ora', ZPG) : 0x05, ('asl', ZPG) : 0x06, ('php', NULL): 0x08, ('ora', IMED): 0x09, ('asl', NULL): 0x0A,                      ('ora', ABSL): 0x0D, ('asl', ABSL): 0x0E,
	('bpl', REL) : 0x10, ('ora', INDY): 0x11,                                           ('ora', ZPGX): 0x15, ('asl', ZPGX): 0x16, ('clc', NULL): 0x18, ('ora', ABSY): 0x19,                                           ('ora', ABSX): 0x1D, ('asl', ABSX): 0x1E,
	('jsr', ABSL): 0x20, ('and', XIND): 0x21,                      ('bit', ZPG) : 0x24, ('and', ZPG) : 0x25, ('rol', ZPG) : 0x26, ('plp', NULL): 0x28, ('and', IMED): 0x29, ('rol', NULL): 0x2A, ('bit', ABSL): 0x2C, ('and', ABSL): 0x2D, ('rol', ABSL): 0x2E,
	('bmi', REL) : 0x30, ('and', INDY): 0x31,                                           ('and', ZPGX): 0x35, ('rol', ZPGX): 0x36, ('sec', NULL): 0x38, ('and', ABSY): 0x39,                                           ('and', ABSX): 0x3D, ('rol', ABSX): 0x3E,
	('rti', NULL): 0x40, ('eor', XIND): 0x41,                                           ('eor', ZPG) : 0x45, ('lsr', ZPG) : 0x46, ('pha', NULL): 0x48, ('eor', IMED): 0x49, ('lsr', NULL): 0x4A, ('jmp', ABSL): 0x4C, ('eor', ABSL): 0x4D, ('lsr', ABSL): 0x4E,
	('bvc', REL) : 0x50, ('eor', INDY): 0x51,                                           ('eor', ZPGX): 0x55, ('lsr', ZPGX): 0x56, ('cli', NULL): 0x58, ('eor', ABSY): 0x59,                                           ('eor', ABSX): 0x5D, ('lsr', ABSX): 0x5E,
	('rts', NULL): 0x60, ('adc', XIND): 0x61,                                           ('adc', ZPG) : 0x65, ('ror', ZPG) : 0x66, ('pla', NULL): 0x68, ('adc', IMED): 0x69, ('ror', NULL): 0x6A, ('jmp', ABSL): 0x6C, ('adc', ABSL): 0x6D, ('ror', ABSL): 0x6E,
	('bvs', REL) : 0x70, ('adc', INDY): 0x71,                                           ('adc', ZPGX): 0x75, ('ror', ZPGX): 0x76, ('sei', NULL): 0x78, ('adc', ABSY): 0x79,                                           ('adc', ABSX): 0x7D, ('ror', ABSX): 0x7E,
	                     ('sta', XIND): 0x81,                      ('sty', ZPG) : 0x84, ('sta', ZPG) : 0x85, ('stx', ZPG) : 0x86, ('dey', NULL): 0x88,                      ('txa', NULL): 0x8A, ('sty', ABSL): 0x8C, ('sta', ABSL): 0x8D, ('stx', ABSL): 0x8E,
	('bcc', REL) : 0x90, ('sta', INDY): 0x91,                      ('sty', ZPGX): 0x94, ('sta', ZPGX): 0x95, ('stx', ZPGX): 0x96, ('tya', NULL): 0x98, ('sta', ABSY): 0x99, ('txs', NULL): 0x9A,                      ('sta', ABSX): 0x9D,
	('ldy', IMED): 0xA0, ('lda', XIND): 0xA1, ('ldx', IMED): 0xA2, ('ldy', ZPG) : 0xA4, ('lda', ZPG) : 0xA5, ('ldx', ZPG) : 0xA6, ('tay', NULL): 0xA8, ('lda', IMED): 0xA9, ('tax', NULL): 0xAA, ('ldy', ABSL): 0xAC, ('lda', ABSL): 0xAD, ('ldx', ABSL): 0xAE,
	('bcs', REL) : 0xB0, ('lda', INDY): 0xB1,                      ('ldy', ZPGX): 0xB4, ('lda', ZPGX): 0xB5, ('ldx', ZPGX): 0xB6, ('clv', NULL): 0xB8, ('lda', ABSY): 0xB9, ('tsx', NULL): 0xBA, ('ldy', ABSX): 0xBC, ('lda', ABSX): 0xBD, ('ldx', ABSX): 0xBE,
	('cpy', IMED): 0xC0, ('cmp', XIND): 0xC1,                      ('cpy', ZPG) : 0xC4, ('cmp', ZPG) : 0xC5, ('dec', ZPG) : 0xC6, ('iny', NULL): 0xC8, ('cmp', IMED): 0xC9, ('dex', NULL): 0xCA, ('cpy', ABSL): 0xCC, ('cmp', ABSL): 0xCD, ('dec', ABSL): 0xCE,
	('bne', REL) : 0xD0, ('cmp', INDY): 0xD1,                                           ('cmp', ZPGX): 0xD5, ('dec', ZPGX): 0xD6, ('cld', NULL): 0xD8, ('cmp', ABSY): 0xD9,                                           ('cmp', ABSX): 0xDD, ('dec', ABSX): 0xDE,
	('cpx', IMED): 0xE0, ('sbc', XIND): 0xE1,                      ('cpx', ZPG) : 0xE4, ('sbc', ZPG) : 0xE5, ('inc', ZPG) : 0xE6, ('inx', NULL): 0xE8, ('sbc', IMED): 0xE9, ('nop', NULL): 0xEA, ('cpx', ABSL): 0xEC, ('sbc', ABSL): 0xED, ('inc', ABSL): 0xEE,
	('beq', REL) : 0xF0, ('sbc', INDY): 0xF1,                                           ('sbc', ZPGX): 0xF5, ('inc', ZPGX): 0xF6, ('sed', NULL): 0xF8, ('sbc', ABSY): 0xF9,                                           ('sbc', ABSX): 0xFD, ('inc', ABSX): 0xFE
}

class Line:
	def __init__(self, pos, line):
		self.pos = pos
		self.line = re.sub(r'\s+$', '', line)

	def __str__(self):
		return self.line

	def __repr__(self):
		return "{}:'{}'".format(self.pos, self.line)

class Token:
	def __init__(self, type_, line_number, start, match):
		self.__type = type_
		self.__line_number = line_number
		self.__start = start
		self.__match = match

	def get_type(self):
		return self.__type

	def get_line_number(self):
		return self.__line_number

	def get_start(self):
		return self.__start

	def get_match(self):
		return self.__match

	def __repr__(self):
		return "{} at {}:{}:'{}'".format(self.__type, self.__line_number, self.__start, re.sub(r'(\r\n|\n|\r)+', '', self.__match))

	__str__ = __repr__

class CharStream:
	def __init__(self, source):
		self.__source = str(source)
		self.__pos = 0

	def accept(self, matcher):
		return matcher(self.__source, self.__pos)

	def consume(self, match):
		self.__pos = match.end()

	def expect(self, matcher):
		match = self.accept(matcher)

		if not match:
			raise Error('Error matching {}'.format(matcher))

		self.consume(match)
		return match

	def hasNext(self):
		return self.__pos < len(self.__source)

	def __str__(self):
		return str(self.__source[self.__pos:])

	__repr__ = __str__

class Tokenizer:
	def __init__(self, source):
		s = re.sub(r';.+', '', source)
		s = s.splitlines(True)

		self.tokens = [self.tokenize(line_number + 1, line) for (line_number, line) in zip(range(len(s)), s)]
		self.tokens = [[token for token in line if token.get_type() != str(SPACE) and token.get_type() != str(EOL)] for line in self.tokens]
		self.tokens = [line for line in self.tokens if len(line) > 0]

	def tokenize(self, line_number, line):
		stream = CharStream(line)
		tokens = []

		while stream.hasNext():
			valid = False

			for matcher in priorities:
				match = stream.accept(matcher)

				if not match:
					continue

				stream.expect(matcher)
				t = Token(str(matcher), line_number, match.start(), match.group())
				tokens.append(t)
				valid = True
				break

			if not valid:
				raise Exception('Unknown:{}'.format(stream))
				break

		return tokens

# TODO Try to make this a generator
class TokenStream:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	def hasNext(self):
		return self.pos < len(self.tokens)

	def get(self):
		return self.tokens[self.pos]

	def accept(self, token):
		return self.get().get_type() == str(token) if self.hasNext() else False

	def __repr__(self):
		return str(self.tokens[self.pos:])
	
	__str__ = __repr__

	def skip(self):
		self.pos += 1

	def expect(self, token):
		if not self.accept(token):
			print(self)
			raise Exception('{} token not found'.format(str(token)))

		# print(token)
		t = self.get()
		self.pos += 1

		return t

class ParserToken:
	def __init__(self, ttype, value=None, line_number=None):
		self.ttype = ttype
		self.value = value
		self.line_number = line_number

	def __repr__(self):
		return "{}{}:'{}'".format(self.ttype, ' at {}'.format(self.line_number) if self.line_number else '', self.value if self.value else '')

	__str__ = __repr__

class Parser:
	def __init__(self, tokens, consts):
		self.consts = {}
		self.labels = {}
		self.addresses = {}
		self.ins_counter = 0
		# self.tokens = [[ParserToken(token) for token in line] for line in tokens]
		self.tokens = tokens
		self.results = []

		for line in self.tokens:
			self.stream = TokenStream(line)
			while self.stream.hasNext():
				if self.stream.accept(DEFINE):
					self.define()
				elif self.stream.accept(MNE):
					self.instruction()
				elif self.stream.accept(ID):
					self.identifier()
				else:
					print(self.stream)
					raise Exception('Syntax error')

		print(self.results)

	def parseInt(self, s):
		b10 = re.match(r'(\d+)', s)
		b16 = re.match(r'\$([0-9a-fA-F]+)', s)
		v = int(b16.group(1), 16) if b16 else int(b10.group(1))

		return v

	def define(self):
		self.stream.expect(DEFINE)
		name = self.stream.expect(ID).get_match()
		value = self.stream.expect(CONST).get_match()

		self.consts[name] = self.parseInt(value)

	def operand(self):
		if self.stream.accept(CONST):
			value = self.stream.expect(CONST).get_match()
			value = self.parseInt(value)

			return value
		
		return self.stream.expect(ID).get_match()

	def indirects(self):
		self.stream.expect(LB)
		value = self.operand()

		if self.stream.accept(RB):
			self.stream.expect(RB)

			if self.stream.accept(YI):
				self.stream.expect(YI)
				return ParserToken(str(INDY)), ParserToken(str(ID) if type(value) is str else str(CONST), value)

			return ParserToken(str(INDR)), ParserToken(str(ID) if type(value) is str else str(CONST), value)
		else:
			self.stream.expect(XI)
			self.stream.expect(RB)
			
			return ParserToken(str(XIND)), ParserToken(str(ID) if type(value) is str else str(CONST), value)

	def immediate(self):
		ln = self.stream.expect(HASH).get_line_number()
		value = self.operand()

		return ParserToken(str(IMED)), ParserToken(str(ID) if type(value) is str else str(CONST), value)

	def instruction(self):
		token = self.stream.expect(MNE)
		self.results.append(ParserToken(str(MNE), token.get_match(), token.get_line_number()))

		self.ins_counter += 1

		if self.stream.accept(HASH):
			vtype, value = self.immediate()
			self.results.append(vtype)
			self.results.append(value)
			return
		elif self.stream.accept(LB):
			vtype, value = self.indirects()
			self.results.append(vtype)
			self.results.append(value)
			return
		elif self.stream.accept(CONST) or self.stream.accept(ID):
			vtype = str(ID) if self.stream.accept(ID) else str(CONST)
			value = self.operand()

			if self.stream.accept(XI):
				self.stream.expect(XI)
				self.results.append(ParserToken(str(X_INDEX)))
				self.results.append(ParserToken(vtype, value))
				return
			elif self.stream.accept(YI):
				self.stream.expect(YI)
				self.results.append(ParserToken(str(Y_INDEX)))
				self.results.append(ParserToken(vtype, value))
				return
			
			self.results.append(ParserToken(str(UNARY)))
			self.results.append(ParserToken(str(ID) if type(value) is str else str(CONST), value))
			return

		self.results.append(ParserToken(str(NULL)))
		return

	def identifier(self):
		name = self.stream.expect(ID).get_match()
		self.stream.expect(COLON)

		self.labels[name] = self.ins_counter

file = open('test.asm')
source = file.read()
tokenizer = Tokenizer(source)
# print(tokenizer.tokens)
parser = Parser(tokenizer.tokens, None)