import re
import itertools

class TokenMatcher:
	def __init__(self, label, regex):
		self.label = label
		self.matcher = re.compile(regex)

	def __call__(self, string, pos=0):
		return self.matcher.match(string, pos)

	def __str__(self):
		return self.label

	__repr__ = __str__

mnemonic = {'ldx', 'lsr', 'rti', 'sta', 'bcs', 'brk', 'sed', 'sec', 'beq', 'cpy', 'pla', 'and', 'tax', 'sty', 'dey', 'inx', 'rts', 'sei', 'bne', 'bvc', 'eor', 'asl', 'cmp', 'txs', 'txa', 'jmp', 'ror', 'nop', 'stx', 'inc', 'iny', 'bvs', 'adc', 'cld', 'pha', 'tya', 'ora', 'plp', 'jsr', 'bit', 'lda', 'bmi', 'tsx', 'rol', 'cpx', 'php', 'dex', 'bpl', 'clv', 'clc', 'dec', 'bcc', 'ldy', 'tay', 'sbc', 'cli'}

DEFINE = TokenMatcher('New const'    , r'\bdefine\b')
ID     = TokenMatcher('Identifier'   , r'[_a-zA-Z][_a-zA-Z0-9]*')
VALUE  = TokenMatcher('Value'        , r'(\d+|\$[0-9a-fA-F]+)\b')
SPACE  = TokenMatcher('Space'        , r'[ \t]+')
COLON  = TokenMatcher('Colon'        , r':')
SCOLON = TokenMatcher('Comment begin', r';')
HASH   = TokenMatcher('Immediate'    , r'#')
HEX    = TokenMatcher('Hex prefix'   , r'\$')
LB     = TokenMatcher('Left bracket' , r'\(')
RB     = TokenMatcher('Right bracket', r'\)')
COMMA  = TokenMatcher('Comma'        , r',')
XI     = TokenMatcher('X index'      , r'\b[Xx]\b')
YI     = TokenMatcher('Y index'      , r'\b[Yy]\b')
EOL    = TokenMatcher('End of line'  , r'\r\n|\r|\n')

instRegex = ''
for m in mnemonic:
	instRegex += '{}|'.format(m)
instRegex = '\\b({})\\b'.format(instRegex[:-1])
INS    = TokenMatcher('Instruction'  , instRegex)

# lineBegin = [DEFINE, SCOLON, ID, IST, EOL]
unambiguous = [INS, HASH, VALUE, ID, XI, YI, COMMA, COLON, LB, RB]

noOp = 'No operand'
imd = 'Immediate'
absl = 'Absolute'
rel = 'Relative'
ind = 'Indirect'
zpg = 'Zero Page'
zpx = 'Zero Page X Indexed'
zpy = 'Zero Page Y Indexed'
xInd = 'X Indirected'
indY = 'Indirected Y'
absX = 'Absolute X Indexed'
absY = 'Absolute Y Indexed'

opcodes = {
	('brk', noOp)	: 0x00,	('ora', xInd): 0x01,                                         ('ora', zpg): 0x05, ('asl', zpg): 0x06, ('php', noOp): 0x08, ('ora', imd)	: 0x09, ('asl', noOp): 0x0A,                        ('ora', absl): 0x0D, ('asl', absl): 0x0E,
	('bpl', rel)	: 0x10,	('ora', indY): 0x11,                                         ('ora', zpx): 0x15, ('asl', zpx): 0x16, ('clc', noOp): 0x18, ('ora', absY)	: 0x19,                                             ('ora', absX): 0x1D, ('asl', absX): 0x1E,
	('jsr', absl)	: 0x20,	('and', xInd): 0x21,                     ('bit', zpg): 0x24, ('and', zpg): 0x25, ('rol', zpg): 0x26, ('plp', noOp): 0x28, ('and', imd)	: 0x29, ('rol', noOp): 0x2A, ('bit', absl)	: 0x2C, ('and', absl): 0x2D, ('rol', absl): 0x2E,
	('bmi', rel)	: 0x30,	('and', indY): 0x31,                                         ('and', zpx): 0x35, ('rol', zpx): 0x36, ('sec', noOp): 0x38, ('and', absY)	: 0x39,                                             ('and', absX): 0x3D, ('rol', absX): 0x3E,
	('rti', noOp)	: 0x40,	('eor', xInd): 0x41,                                         ('eor', zpg): 0x45, ('lsr', zpg): 0x46, ('pha', noOp): 0x48, ('eor', imd)	: 0x49, ('lsr', noOp): 0x4A, ('jmp', absl)	: 0x4C, ('eor', absl): 0x4D, ('lsr', absl): 0x4E,
	('bvc', rel)	: 0x50,	('eor', indY): 0x51,                                         ('eor', zpx): 0x55, ('lsr', zpx): 0x56, ('cli', noOp): 0x58, ('eor', absY)	: 0x59,                                             ('eor', absX): 0x5D, ('lsr', absX): 0x5E,
	('rts', noOp)	: 0x60,	('adc', xInd): 0x61,                                         ('adc', zpg): 0x65, ('ror', zpg): 0x66, ('pla', noOp): 0x68, ('adc', imd)	: 0x69, ('ror', noOp): 0x6A, ('jmp', absl)	: 0x6C, ('adc', absl): 0x6D, ('ror', absl): 0x6E,
	('bvs', rel)	: 0x70,	('adc', indY): 0x71,                                         ('adc', zpx): 0x75, ('ror', zpx): 0x76, ('sei', noOp): 0x78, ('adc', absY)	: 0x79,                                             ('adc', absX): 0x7D, ('ror', absX): 0x7E,
	                        ('sta', xInd): 0x81,                     ('sty', zpg): 0x84, ('sta', zpg): 0x85, ('stx', zpg): 0x86, ('dey', noOp): 0x88,                       ('txa', noOp): 0x8A, ('sty', absl)	: 0x8C, ('sta', absl): 0x8D, ('stx', absl): 0x8E,
	('bcc', rel)	: 0x90,	('sta', indY): 0x91,                     ('sty', zpx): 0x94, ('sta', zpx): 0x95, ('stx', zpx): 0x96, ('tya', noOp): 0x98, ('sta', absY)	: 0x99, ('txs', noOp): 0x9A,                        ('sta', absX): 0x9D,
	('ldy', imd)	: 0xA0,	('lda', xInd): 0xA1, ('ldx', imd): 0xA2, ('ldy', zpg): 0xA4, ('lda', zpg): 0xA5, ('ldx', zpg): 0xA6, ('tay', noOp): 0xA8, ('lda', imd)	: 0xA9, ('tax', noOp): 0xAA, ('ldy', absl)	: 0xAC, ('lda', absl): 0xAD, ('ldx', absl): 0xAE,
	('bcs', rel)	: 0xB0,	('lda', indY): 0xB1,                     ('ldy', zpx): 0xB4, ('lda', zpx): 0xB5, ('ldx', zpx): 0xB6, ('clv', noOp): 0xB8, ('lda', absY)	: 0xB9, ('tsx', noOp): 0xBA, ('ldy', absX)	: 0xBC, ('lda', absX): 0xBD, ('ldx', absX): 0xBE,
	('cpy', imd)	: 0xC0,	('cmp', xInd): 0xC1,                     ('cpy', zpg): 0xC4, ('cmp', zpg): 0xC5, ('dec', zpg): 0xC6, ('iny', noOp): 0xC8, ('cmp', imd)	: 0xC9, ('dex', noOp): 0xCA, ('cpy', absl)	: 0xCC, ('cmp', absl): 0xCD, ('dec', absl): 0xCE,
	('bne', rel)	: 0xD0,	('cmp', indY): 0xD1,                                         ('cmp', zpx): 0xD5, ('dec', zpx): 0xD6, ('cld', noOp): 0xD8, ('cmp', absY)	: 0xD9,                                             ('cmp', absX): 0xDD, ('dec', absX): 0xDE,
	('cpx', imd)	: 0xE0,	('sbc', xInd): 0xE1,                     ('cpx', zpg): 0xE4, ('sbc', zpg): 0xE5, ('inc', zpg): 0xE6, ('inx', noOp): 0xE8, ('sbc', imd)	: 0xE9, ('nop', noOp): 0xEA, ('cpx', absl)	: 0xEC, ('sbc', absl): 0xED, ('inc', absl): 0xEE,
	('beq', rel)	: 0xF0,	('sbc', indY): 0xF1,                                         ('sbc', zpx): 0xF5, ('inc', zpx): 0xF6, ('sed', noOp): 0xF8, ('sbc', absY)	: 0xF9,                                             ('sbc', absX): 0xFD, ('inc', absX): 0xFE
}

class Line:
	def __init__(self, pos, line):
		self.pos = pos
		self.line = re.sub(r'\s+$', '', line)

	def __str__(self):
		return self.line

	def __repr__(self):
		return "{}:'{}'".format(self.pos, self.line)

class Preprocessor:
	def __init__(self, source):
		self.consts = {}

		self.lines = source.splitlines(True)
		self.lines = [Line(n, line) for (n, line) in zip(range(1, len(self.lines) + 1), self.lines)]
		self.lines = [Line(line.pos, line.line) for line in self.lines]
		self.lines = [Line(line.pos, line.line[:len(line.line) if line.line.find(';') == -1 else line.line.find(';')]) for line in self.lines]
		defines = [re.split(r'\s+', line.line.strip()) for line in self.lines if line.line.startswith('define')]
		self.lines = [line for line in self.lines if not line.line.startswith('define')]
		self.lines = [line for line in self.lines if len(line.line) > 0]
		
		# TODO check names and values

		for const in defines:
			self.consts[const[1]] = const[2]

class Token:
	def __init__(self, line, start, string):
		self.tokenType = None
		self.line = line
		self.start = start
		self.string = re.sub(r'[ \t]+', '', string)

	def __repr__(self):
		string = re.sub(r'[\r\n]+', '', self.string)

		return "{} at {}:{}:'{}'".format(self.tokenType, self.line, self.start, string)

	__str__ = __repr__

class TokenStream:
	def __init__(self, line):
		self.pos = 0
		self.source = str(line)

	# def equals(self, s):
	# 	r = '\\b{}\\b'.format(s)

	# 	return re.match(r, self.pos)

	def accept(self, matcher):
		return matcher(self.source, self.pos)

	def consume(self, match):
		self.pos = match.end()

	def expect(self, matcher):
		match = self.accept(matcher)

		if not match:
			raise Error('Error trying to match')

		self.consume(match)

	def hasNext(self):
		return self.pos < len(self.source)

	def __str__(self):
		return str(self.source[self.pos:])

	__repr__ = __str__

class Tokenizer:
	def __init__(self, lines):
		self.lines = [self.tokenizeLine(line) for line in lines]
		print(self.lines)

	def tokenizeLine(self, line):
		stream = TokenStream(line)
		tokens = []

		while stream.hasNext():
			if stream.accept(SPACE):
				stream.expect(SPACE)
				continue

			valid = False

			for matcher in unambiguous:
				match = stream.accept(matcher)

				if not match:
					continue

				stream.expect(matcher)
				t = Token(line.pos, match.start(), match.group())
				t.tokenType = matcher.label
				tokens.append(t)
				valid = True
				break

			if not valid:
				print('Unknown:{}'.format(stream))
				break

		return tokens

class Parser:
	def __init__(self, tokens):
		pass

	def parseDefine(self):
		self.tokens.expect(WORD)

		if WORD in self.consts:
			raise Exception('Redefinition of "%s"' % self.tokens.tokens[self.tokens.i])

		self.consts[WORD] = []

		if self.tokens.accept(HASH):
			pass

		if self.tokens.accept(HEX):
			pass

		if self.tokens.accept(VALUE):
			pass

	def parseLabel(self):
		self.tokens.expect(COLON)

		if self.tokens.accept(INS):
			self.parseInstruction()

	def parseOperand(self):
		pass

	def parseNumber(self):
		pass

	def parseInstruction(self):
		pass

	def parseLine(self):
		if self.tokens.accept(EOL):
			pass
		elif self.tokens.accept(DEFINE):
			self.parseDefine()
			self.tokens.expect(EOL)
		elif self.tokens.accept(WORD):
			self.parseLabel()
			self.tokens.expect(EOL)
		elif self.tokens.accept(INS):
			self.parseInstruction()
			self.tokens.expect(EOL)
		else:
			raise Exception('Syntax error: "%s"' % self.tokens.tokens[self.tokens.i])

	def parseProgram(self):
		while not self.tokens.empty():
			self.parseLine()
			# self.tokens.expect(EOL)

class Instruction:
	def __init__(self, instruction, addrMode, operand):
		self.instruction = instruction
		self.addrMode = addrMode
		self.operand = operand

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '[%s, %s, %s]' % (self.instruction, self.addrMode, self.operand)

class CodeGenerator:
	# coming soon. Hopefully...
	pass

file = open('test.asm')
source = file.read()
preprocessor = Preprocessor(source)
# print(preprocessor.lines)
tokenizer = Tokenizer(preprocessor.lines)
# parser = Parser(lexer.tokens)
# print(parser.consts)
# print(parser.mnemonic)
# print(len(parser.mnemonic))
# print()
# print(parser.opcodes)