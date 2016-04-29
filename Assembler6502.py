from enum import Enum
import re

class Tokens(Enum):
	MNEMONIC      = 0
	DEFINE        = 1
	IDENTIFIER    = 2
	CONSTANT      = 3
	SPACES        = 4
	COLON         = 5
	HASH          = 6
	LEFT_BRACKET  = 7
	RIGHT_BRACKET = 8
	X_INDEX       = 9
	Y_INDEX       = 10
	NEWLINE       = 11
	BAD_TOKEN     = 12

	def __str__(self):
		return self.name

	__repr__ = __str__

class TokenMatcher:
	def __init__(self, type_, matcher, trivial=True):
		self.__type = type_
		self.__matcher = matcher
		self.__trivial = trivial

	def is_trivial(self):
		return self.__trivial

	def match(self, string, pos=0):
		return self.__matcher.match(string, pos)

	def get_type(self):
		return self.__type

	def __str__(self):
		return str(self.get_type())

	__repr__ = __str__

mnemonic = {'ldx', 'lsr', 'rti', 'sta', 'bcs', 'brk', 'sed', 'sec', 'beq', 'cpy', 'pla', 'and', 'tax', 'sty', 'dey', 'inx', 'rts', 'sei', 'bne', 'bvc', 'eor', 'asl', 'cmp', 'txs', 'txa', 'jmp', 'ror', 'nop', 'stx', 'inc', 'iny', 'bvs', 'adc', 'cld', 'pha', 'tya', 'ora', 'plp', 'jsr', 'bit', 'lda', 'bmi', 'tsx', 'rol', 'cpx', 'php', 'dex', 'bpl', 'clv', 'clc', 'dec', 'bcc', 'ldy', 'tay', 'sbc', 'cli'}
instRegex = ''
for m in mnemonic:
	instRegex += '{}|'.format(m)
instRegex = '\\b({})\\b'.format(instRegex[:-1])

MNE   = TokenMatcher(Tokens.MNEMONIC     , re.compile(instRegex, flags=re.IGNORECASE), trivial=False)
DEF   = TokenMatcher(Tokens.DEFINE       , re.compile(r'\bdefine\b'))
ID    = TokenMatcher(Tokens.IDENTIFIER   , re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*'), trivial=False)
CONST = TokenMatcher(Tokens.CONSTANT     , re.compile(r'(\d+|\$[0-9a-fA-F]+)\b'), trivial=False)
SPACE = TokenMatcher(Tokens.SPACES       , re.compile(r'[ \t]+'))
COLON = TokenMatcher(Tokens.COLON        , re.compile(r':'))
HASH  = TokenMatcher(Tokens.HASH         , re.compile(r'#'))
LB    = TokenMatcher(Tokens.LEFT_BRACKET , re.compile(r'\('))
RB    = TokenMatcher(Tokens.RIGHT_BRACKET, re.compile(r'\)'))
XI    = TokenMatcher(Tokens.X_INDEX      , re.compile(r',\s*[Xx]\b'))
YI    = TokenMatcher(Tokens.Y_INDEX      , re.compile(r',\s*[Yy]\b'))
EOL   = TokenMatcher(Tokens.NEWLINE      , re.compile(r'\r\n|\r|\n'))
ERR   = TokenMatcher(Tokens.BAD_TOKEN    , re.compile(r'.'))

priorities = [EOL, MNE, DEF, ID, SPACE, HASH, CONST, XI, YI, COLON, LB, RB, ERR]

UNARY   = 'Unary'
X_INDEX = 'X indexed'
Y_INDEX = 'Y indexed'
INDEX = 'INDEX'

NULL = 'Nullary'
IMED = 'Immediate'
ABSL = 'Absolute'
REL  = 'Relative'
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
	('rts', NULL): 0x60, ('adc', XIND): 0x61,                                           ('adc', ZPG) : 0x65, ('ror', ZPG) : 0x66, ('pla', NULL): 0x68, ('adc', IMED): 0x69, ('ror', NULL): 0x6A, ('jmp', INDR): 0x6C, ('adc', ABSL): 0x6D, ('ror', ABSL): 0x6E,
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

class Token:
	def __init__(self, type_, value=None, origin=None):
		self.__type = type_
		self.__value = value
		self.__origin = origin

	def get_type(self):
		return self.__type

	def get_value(self):
		return self.__value

	def __repr__(self):
		location = ' at {}'.format(self.__origin) if self.__origin is not None else ''
		value = ":'{}'".format(self.__value) if self.__value is not None else ''

		return '{}{}{}'.format(self.__type, location, value)

	__str__ = __repr__

class CharStream:
	def __init__(self, source):
		self.__source = str(source)
		self.__pos = 0

	def accept(self, matcher):
		return matcher.match(self.__source, self.__pos)

	def __consume(self, match):
		self.__pos = match.end()

	def expect(self, matcher):
		match = self.accept(matcher)

		if not match:
			raise Error('Error matching {}'.format(matcher))

		self.__consume(match)
		return match

	def has_next(self):
		return self.__pos < len(self.__source)

	def __str__(self):
		return str(self.__source[self.__pos:])

	__repr__ = __str__

class Tokenizer:
	def __init__(self, source):
		s = re.sub(r';.*', '', source)
		s = s.splitlines(True)

		self.tokens = [self.tokenize(line_number, line) for (line_number, line) in zip(range(len(s) + 1), s)]
		self.tokens = [[token for token in line if token.get_type() not in {Tokens.SPACES, Tokens.NEWLINE}] for line in self.tokens]
		self.tokens = [line for line in self.tokens if len(line) > 0]

	def tokenize(self, line_number, line):
		stream = CharStream(line)
		tokens = []

		while stream.has_next():
			for matcher in priorities:
				match = stream.accept(matcher)

				if matcher is ERR:
					raise Exception('Unknown:{}'.format(stream))
					break

				if not match:
					continue

				stream.expect(matcher)
				t = Token(matcher.get_type(), None if matcher.is_trivial() else match.group())
				tokens.append(t)
				break

		return tokens

class TokenStream:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	def has_next(self):
		return self.pos < len(self.tokens)

	def get(self):
		return self.tokens[self.pos]

	def accept(self, token):
		return self.get().get_type() is token if self.has_next() else False

	def __repr__(self):
		return str(self.tokens[self.pos:])
	
	__str__ = __repr__

	def skip(self):
		t = self.get()
		self.pos += 1

		return t

	def expect(self, token):
		# print(token)
		if not self.accept(token):
			print(self)
			raise Exception('{} token not found'.format(str(token)))

		t = self.get()
		self.pos += 1

		return t

class Parser:
	def __init__(self, tokens, consts):
		self.labels = {}
		self.addresses = {}
		self.ins_counter = 0
		self.tokens = tokens
		self.results = []

		for line in self.tokens:
			self.stream = TokenStream(line)

			while self.stream.has_next():
				if self.stream.accept(Tokens.DEFINE):
					self.define()
				elif self.stream.accept(Tokens.MNEMONIC):
					self.instruction()
				elif self.stream.accept(Tokens.IDENTIFIER):
					self.label()
				else:
					print(self.stream)
					raise Exception('Syntax error')

		# print(self.results)

	def emit(self, token):
		self.results.append(token)

	def define(self):
		self.stream.expect(Tokens.DEFINE)
		name = self.stream.expect(Tokens.IDENTIFIER).get_value()
		value = self.stream.expect(Tokens.CONSTANT).get_value()
		self.emit(Token(Tokens.DEFINE, (name, value)))

	def operand(self):
		return self.stream.expect(Tokens.CONSTANT) if self.stream.accept(Tokens.CONSTANT) else self.stream.expect(Tokens.IDENTIFIER)

	def indirects(self):
		self.stream.expect(Tokens.LEFT_BRACKET)
		param = self.operand()

		if self.stream.accept(Tokens.RIGHT_BRACKET):
			self.stream.expect(Tokens.RIGHT_BRACKET)

			if self.stream.accept(Tokens.Y_INDEX):
				self.stream.expect(Tokens.Y_INDEX)
				self.emit(Token(INDY))
			else:
				self.emit(Token(INDR))
		else:
			self.stream.expect(Tokens.X_INDEX)
			self.stream.expect(Tokens.RIGHT_BRACKET)
			self.emit(Token(XIND))

		self.emit(param)

	def immediate(self):
		self.stream.expect(Tokens.HASH)
		param = self.operand()
		self.emit(Token(IMED))
		self.emit(param)

	def instruction(self):
		self.emit(self.stream.expect(Tokens.MNEMONIC))

		self.ins_counter += 1

		if self.stream.accept(Tokens.HASH):
			self.immediate()
			return
		elif self.stream.accept(Tokens.LEFT_BRACKET):
			self.indirects()
			return
		elif self.stream.accept(Tokens.CONSTANT) or self.stream.accept(Tokens.IDENTIFIER):
			operand = self.operand()

			if self.stream.accept(Tokens.X_INDEX):
				self.stream.expect(Tokens.X_INDEX)
				self.emit(Token(ABSX))
				self.emit(operand)
				return
			elif self.stream.accept(Tokens.Y_INDEX):
				self.stream.expect(Tokens.Y_INDEX)
				self.emit(Token(ABSY))
				self.emit(operand)
				return
			
			self.emit(Token(UNARY))
			self.emit(operand)
			return

		self.emit(Token(NULL))
		return

	def label(self):
		name = self.stream.expect(Tokens.IDENTIFIER).get_value()
		self.stream.expect(Tokens.COLON)

		self.labels[name] = self.ins_counter

# need polish
# change member names
# add addr member
# remove opcode member
# make private
# add accessors and modifiers
class Instruction:
	def __init__(self, mnemonic, mode, value=None, line_number=None):
		self.mnemonic = mnemonic
		self.mode = mode
		self.value = value
		self.line_number = line_number
		self.opcode = 0
		self.size = 0

	def __repr__(self):
		if self.mode is NULL:
			return str(self.mnemonic)

		# return str((str(self.mnemonic), str(self.mode), str(self.value), self.addr))
		return str((str(self.mnemonic), str(self.mode), str(self.value)))

class SemanticAnalyzer:
	def __init__(self, parser_tokens, labels):
		self.tokens = parser_tokens
		self.labels = labels
		self.consts = {}

		self.check_ids()
		self.substitute_ids()
		self.deduce()
		self.compute_size_and_addr()
		# print(self.consts)
		# print(self.labels)
		self.compute_params()
		self.binary = []
		self.generate_code()
		# print(self.results)
		# [print(hex(x)) for x in self.binary]
		self.binary = bytes(self.binary)
		out = open('out.bin', 'wb')
		out.write(self.binary)

	def check_ids(self):
		stream = TokenStream(self.tokens)

		while stream.has_next():
			# check for redefinition
			if stream.accept(Tokens.DEFINE):
				token = stream.expect(Tokens.DEFINE)
				name, value = token.get_value()
				self.check_redefinition(name, value)
				self.consts[name] = self.parse_int(value)
			elif stream.accept(Tokens.IDENTIFIER):
				name = stream.expect(Tokens.IDENTIFIER).get_value()
				self.check_undecl_ids(name)
			else:
				stream.skip()

	def substitute_ids(self):
		stream = TokenStream(self.tokens)

		tokens = []

		while stream.has_next():
			if stream.accept(Tokens.DEFINE):
				stream.skip()
			elif stream.accept(Tokens.IDENTIFIER):
				token = stream.expect(Tokens.IDENTIFIER)
				t = token.get_type()
				name = token.get_value()

				# polish this block
				type_ = INDEX if name in self.labels else Tokens.CONSTANT
				value = self.labels[name] if name in self.labels else self.consts[name]

				tokens.append(Token(type_, value))
			# remove this hack. Parse values when appropriate
			elif stream.accept(Tokens.CONSTANT):
				token = stream.expect(Tokens.CONSTANT)
				tokens.append(Token(Tokens.CONSTANT, self.parse_int(token.get_value())))
			else:
				tokens.append(stream.skip())

		self.results = tokens

	def deduce(self):
		stream = TokenStream(self.results)
		tokens = []

		while stream.has_next():
			mne = stream.expect(Tokens.MNEMONIC).get_value().lower()
			mode = stream.skip().get_type()
			# look into fixing inconsistency due to the lack of get_type() here
			param = stream.skip() if mode is not NULL else None

			# print(mne, self.deduce_mode(mne, mode, param), param)
			tokens.append(Instruction(mne, self.deduce_mode(mne, mode, param), param))

		self.results = tokens

	def deduce_mode(self, mne, mode, param):
		# print(mne, mode, param)
		if mode not in {UNARY, ABSX, ABSY}:
			return mode

		# hack due to inconsistency from previous stage
		param = param.get_value()

		if (mne, REL) in opcodes:
			# print(mne, REL, type(param), param)
			return REL

		if mode is UNARY:
			if (mne, ZPG) in opcodes and param <= 0xFF:
				return ZPG
			else:
				return ABSL

		if mode is ABSX:
			if (mne, ZPGX) in opcodes and param <= 0xFF:
				return ZPGX
			else:
				return ABSX

		if mode is ABSY:
			if (mne, ZPGY) in opcodes and param <= 0xFF:
				return ZPGY
			else:
				return ABSY

	def parse_int(self, s):
		return int(s[1:], 16) if s[0] == '$' else int(s)

	def check_redefinition(self, name, value):
		if name in self.consts:
			raise Exception("{} has already been defined as {}".format(name, self.consts[name]))

		if name in self.labels:
			raise Exception("{} is a label".format(name))

	def check_undecl_ids(self, var_name):
		if var_name not in self.consts and var_name not in self.labels:
			raise Exception("Use of undeclared variable '{}'".format(var_name))

	def compute_size_and_addr(self):
		addr = 0x600

		for instruction in self.results:
			mode = instruction.mode
			instruction.addr = addr

			if mode is NULL:
				instruction.size = 1
			elif mode in {ABSL, ABSX, ABSY, INDR}:
				instruction.size = 3
			else:
				instruction.size = 2

			addr += instruction.size

		self.end = addr

	def compute_params(self):
		for instruction in self.results:
			# Fix this big hack
			if instruction.value is not None and type(instruction.value) is not int and instruction.value.get_type() is Tokens.CONSTANT:
				instruction.value = instruction.value.get_value()
				continue

			if instruction.mode in {IMED, NULL}:
				continue

			if instruction.value.get_type() is not INDEX:
				continue

			if instruction.mode is REL:
				dest = self.results[instruction.value.get_value()].addr
				diff = dest - (instruction.addr + instruction.size)

				instruction.value = diff
				if diff not in range(-128, 128):
					raise Exception('Attempting to jump too far')
			else:
				# print(instruction.value.get_value(), instruction, len(self.results))

				index = instruction.value.get_value()
				instruction.value = self.results[index].addr if index < len(self.results) else self.end
				# print(type(instruction.value))

	def generate_code(self):
		for instruction in self.results:
			self.generate_instruction(instruction)

	def generate_instruction(self, instruction):
		key = (instruction.mnemonic, instruction.mode)
		opcode = opcodes[key]
		mode = instruction.mode
		param = instruction.value

		self.binary.append(opcode)

		if mode in {ABSL, ABSX, ABSY, INDR}:
			self.generate_word(param)
		elif mode is REL:
			self.generate_complement(param)
		elif mode != NULL:
			self.binary.append(param)

	def generate_word(self, n):
		low = n % 0x100
		high = n // 0x100

		self.binary.append(low)
		self.binary.append(high)

	def generate_complement(self, n):
		if n < 0:
			self.binary.append(0xFF + n + 1)
		else:
			self.binary.append(n)

file = open('test5.asm')
source = file.read()
tokenizer = Tokenizer(source)
# print(tokenizer.tokens)
parser = Parser(tokenizer.tokens, None)
# print(parser.results)
analyzer = SemanticAnalyzer(parser.results, parser.labels)