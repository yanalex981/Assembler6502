import re

DEF, ID, INS, CONST, COL, HASH, CMA, LB, RB, IREG, COMMENT, NEWLINE, BLANK = 'DEFINE', 'IDENTIFIER', 'INSTRUCTION', 'CONSTANT', 'COLON', 'HASH', 'COMMA', 'LEFT BRACKET', 'RIGHT BRACKET', 'INDEX REGISTER', 'COMMENT', 'NL', 'BLANK'
skip = {COMMENT, BLANK}
priorities = [DEF, INS, ID, COMMENT, NEWLINE, BLANK, IREG, COL, RB, LB, CMA, HASH, CONST]

tokens = {
	DEF    : r'\bdefine\b',
	ID     : r'\b([a-zA-z_]\w+)\b',
	INS    : r'\b([a-zA-Z]{3})\b',
	CONST  : r'\b([0-9a-fA-F]+)\b|(\$[0-9a-fA-F]+)\b|(#\$[0-9a-fA-F]+)\b',
	COL    : r':',
	HASH   : r'#',
	CMA    : r',',
	LB     : r'\(',
	RB     : r'\)',
	IREG   : r'\b([xXyY])\b',
	COMMENT: r';.+',
	NEWLINE: r'\r\n|\r|\n',
	BLANK  : r'\s+'
}

valuables = {ID, INS, CONST, IREG}

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

class Token:
	def __init__(self, tokenType, value = None):
		self.tokenType = tokenType
		self.value = value

	def __repr__(self):
		if self.value == None:
			return '%s' % self.tokenType

		return '%s: "%s"' % (self.tokenType, self.value)

class Tokenizer:
	def __init__(self, source):
		self.source = source
		self.patterns = {}

		for token in tokens:
			pattern = tokens[token]
			self.patterns[token] = re.compile(pattern)

		self.tokenize()
		self.sanitize()

	def tokenize(self):
		self.tokenStream = []

		begin = 0
		while begin < len(self.source):
			valid = False

			for token in priorities:
				pattern = tokens[token]
				matcher = re.compile(pattern)
				match = matcher.match(self.source, begin)

				if not match:
					continue

				valid = True
				begin = match.end()

				if token in skip:
					break

				tokenObj = Token(token) if token not in valuables else Token(token, match.group())

				self.tokenStream.append(tokenObj)
				break

			if not valid:
				end = self.patterns[NEWLINE].search(self.source, begin)
				raise Exception('Bad token: "%s"' % self.source[begin:end.span()[0]])

	def sanitize(self):
		tokenStream = []

		while self.tokenStream[0].tokenType == NEWLINE:
			self.tokenStream.pop(0)

		for token in self.tokenStream:
			if len(tokenStream) == 0:
				tokenStream.append(token)
				continue

			if tokenStream[-1].tokenType == NEWLINE and tokenStream[-1].tokenType == token.tokenType:
				continue

			tokenStream.append(token)

		self.tokenStream = tokenStream

class Parser:
	def __init__(self, tokens):
		self.binary = []
		self.constants = {}
		self.labels = {}
		self.subParsers = {
			DEF: self.parseDefine,
			ID : self.parseID,
			INS: self.parseInstruction,
			CONST: self.parseHex
		}

		self.parse()

	def parseDefine(self, tokens):
		tokens.pop(0)

		if tokens[0].tokenType != 'ID':
			raise Exception('Expected an identifier, got "%s" instead' % tokens[0])

		name = tokens[0].value
		tokens.pop(0)

		token = ""

		if tokens[0].value == '#':
			token += '#'
			tokens.pop(0)

		if tokens[0].value == '$':
			token += '$'
			tokens.pop(0)

		token += tokens[0].value
		tokens.pop(0)

		if len(tokens) > 0:
			print("There are still unconsumed tokens on this line. They will be ignored")

		self.constants[name] = token

	def parseNumber(self, token):
		if token.tokenType != 'NBR':
			raise Exception('"%s" Is not a valid number' % token)

		number = token.value

		if number[0] == '$':
			return int(token.value[1:], 16)

		else:
			return int(token.value, 16)

	def parseID(self, tokens):
		if tokens[0].tokenType != 'ID':
			raise Exception('"%s" Is not a valid identifier' % tokens[0])

		name = tokens[0].value
		tokens.pop(0)

		if tokens[0].tokenType != 'COL':
			raise Exception('Expected a :')

		if name in self.labels:
			raise Exception('Label: %s already exists' % name)

		self.labels[name] = len(self.binary)

	def parseOperand(self, tokens):
		print('  %s' % tokens)
		if len(tokens) == 0:
			return (self.noOp, 0)

		stream = []

		for token in tokens:
			if token.tokenType == 'ID':
				name = token.value
				t = None

				if name in self.labels:
					t = Token('NBR', '$%s' % str(self.labels[token.value]).zfill(4))
				elif name in self.constants:
					t = Token('NBR', str(self.constants[token.value]))
				else:
					t = Token('NBR', str(-1))
				# print(t)

				stream.append(t)
			else:
				stream.append(token)

		print('  %s' % stream)

		# stream.pop(0)

		if stream[0].tokenType == 'LIT':
			# print('  %s' % stream)
			stream.pop(0)
			operand = stream[0]
			# print('  %s' % stream)

			# if operand.tokenType == 'ID':
			# 	return (self.imd, self.constants[operand.value])
			return (self.imd, self.parseNumber(operand))

		operand = stream[0]

		if operand.tokenType == 'NBR':
			if len(operand.value) == 3:
				return (self.rel, self.parseNumber(operand))
			else:
				return (self.absl, self.parseNumber(operand))

		if operand.tokenType == 'LB':
			print(stream)
			stream.pop(0)
			operand = stream[0]

			if stream[0] == 'CMA':
				return (self.xInd, self.parseNumber(operand))
			elif stream[0] == 'RB':
				return (self.indY, self.parseNumber(operand))
			else:
				stream.pop(0)
				return (self.ind, self.parseNumber(operand))

	def parseInstruction(self, tokens):
		print(tokens)
		instruction = tokens[0]
		tokens.pop(0)

		# print(instruction)

		mode = self.parseOperand(tokens)
		key = (instruction.value, mode[0])

		if not (key in self.opcodes) and mode[0] == self.rel:
			key = (key[0], self.absl)

		if not (key in self.opcodes) and mode[0] == self.absl:
			key = (key[0], self.rel)

		print(key)

		print(self.opcodes[key])

	def parseHex(self, token):
		return int(token.value, 16)

	def parse(self):
		pass
		# for line in lines:
		# 	self.parseLine(line)

	def parseLine(self, line):
		self.subParsers[line[0].tokenType](line)

file = open('test.asm')
source = file.read()
tokenizer = Tokenizer(source)
print(tokenizer.tokenStream)
# print()
parser = Parser(tokenizer.tokenStream)
# print(parser.constants)
# print()
# print(parser.labels)
# print()
# print(parser.opcodes)