import re

KEYWORD, INS, TEXT, INT, HASH, HEX, COLON, COMMA, LB, RB, SCOLON, NEWLINE, SPACE, ETC, Xreg, Yreg = 'KEYWORD', 'INSTRUCTION', 'TEXT', 'INTEGER', 'HASH', 'HEX', 'COLON', 'COMMA', 'LEFT BRACKET', 'RIGHT BRACKET', 'SEMICOLON', 'NEWLINE', 'SPACE', 'ETC', 'X Index', 'Y INDEX'
priorities = [KEYWORD, INT, TEXT, NEWLINE, SPACE, COLON, RB, LB, COMMA, HASH, SCOLON, HEX, ETC]

tokens = {
	KEYWORD: r'\bdefine\b',
	TEXT   : r'\b\w+\b',
	INT    : r'\b[0-9a-fA-F]+\b',
	HASH   : r'#',
	SCOLON : r';',
	Xreg   : r',[xX]',
	Yreg   : r',[yY]',
	COMMA  : r',',
	COLON  : r':',
	ETC    : r'.+',
	HEX    : r'\$',
	LB     : r'\(',
	RB     : r'\)',
	NEWLINE: r'\r\n|\r|\n',
	SPACE : r'[ \t]+',
}

# valuables = {TEXT, INS, INT, MOD, IREG}
valuables = {TEXT, INT}

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

instructions = {'lsr', 'rti', 'sta', 'bcs', 'brk', 'sed', 'sec', 'beq', 'cpy', 'pla', 'and', 'tax', 'sty', 'dey', 'inx', 'rts', 'sei', 'bne', 'bvc', 'eor', 'asl', 'cmp', 'txs', 'txa', 'jmp', 'ror', 'nop', 'stx', 'inc', 'iny', 'bvs', 'adc', 'cld', 'pha', 'tya', 'ora', 'plp', 'jsr', 'bit', 'lda', 'bmi', 'tsx', 'rol', 'cpx', 'php', 'dex', 'bpl', 'clv', 'clc', 'dec', 'bcc', 'ldy', 'tay', 'sbc', 'cli'}

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
	def __init__(self, line, span, tokenType, value = None):
		self.tokenType = tokenType
		self.value = value
		self.line = line
		self.begin = span[0]
		self.end = span[1]

	def __repr__(self):
		if self.value == None:
			return '%s %i:%i,%i' % (self.tokenType, self.line, self.begin, self.end)

		return '%s %i:%i,%i: "%s"' % (self.tokenType, self.line, self.begin, self.end, re.sub(r'\r|\n', '', self.value))

class Tokenizer:
	def __init__(self, source):
		self.source = source
		self.patterns = {}

		for token in tokens:
			pattern = tokens[token]
			self.patterns[token] = re.compile(pattern)

		self.lines = source.splitlines(True)

		self.tokenize()

	def tokenize(self):
		self.tokenStream = []

		linePos = 1
		for line in self.lines:
			begin = 0
			valid = False
			while begin < len(line):
				for tokenType in priorities:
					pattern = self.patterns[tokenType]
					match = pattern.match(line, begin)

					if not match:
						continue

					valid = True
					begin = match.end()
					tokenObj = Token(linePos, match.span(), tokenType, match.group()) if tokenType in valuables else Token(linePos, match.span(), tokenType)
					self.tokenStream.append(tokenObj)
					break

				if not valid:
					print("Not found...")
					break

			linePos += 1

class Lexer:
	def __init__(self, tokens):
		self.tokens = tokens

		self.stripComments()
		self.stripHeadTail()
		self.stripSpaces()
		self.textToInstructions()
		self.textToIndex()

	def stripSpaces(self):
		self.tokens = [token for token in self.tokens if token.tokenType != SPACE]

	def stripHeadTail(self):
		i = 0
		while self.tokens[i].tokenType == NEWLINE:
			self.tokens.pop(0)

		i = len(self.tokens) - 1
		while self.tokens[i].tokenType == NEWLINE:
			self.tokens.pop()

	def stripComments(self):
		tokens = []
		skip = False

		for token in self.tokens:
			if token.tokenType == SCOLON:
				skip = True
			elif token.tokenType == NEWLINE:
				skip = False

			if not skip:
				tokens.append(token)

		self.tokens = tokens

	def textToIndex(self):
		commaPassed = False
		for token in self.tokens:
			if token.tokenType == COMMA:
				commaPassed = True
			else:
				if token.tokenType == TEXT and commaPassed:
					if token.value.lower() == 'x':
						token.tokenType = Xreg
					elif token.value.lower() == 'y':
						token.tokenType = Yreg

				commaPassed = False

	def textToInstructions(self):
		if self.tokens[0].tokenType == TEXT and self.tokens[0].value in instructions:
			self.tokens[0].tokenType == INS

		newlinePassed = False
		for token in self.tokens:
			if token.tokenType == NEWLINE:
				newlinePassed = True
			else:
				if token.tokenType == TEXT and newlinePassed:
					if token.value in instructions:
						token.tokenType = INS

				newlinePassed = False

class TokenStream:
	def __init__(self, tokens):
		self.tokens = tokens
		self.i = 0

	def peek(self, symbol):
		return True if self.tokens[self.i].tokenType == symbol else False

	def backtrack(self):
		if self.i > 0:
			self.i -= 1

	# return a Newline when reached end of line
	def accept(self, symbol):
		if self.peek(symbol):
			self.i += 1

			return True

		return False

	def expect(self, symbol):
		if self.accept(symbol):
			return True

		raise Exception('%s expected, but encountered %s instead' % (symbol, self.tokens[self.i]))

	def next(self):
		self.i += 1

	def empty(self):
		return self.size() == 0

	def size(self):
		return len(self.tokens)

class Parser:
	def __init__(self, tokens):
		self.tokens = TokenStream(tokens)
		self.consts = {}
		self.lines = []
		self.labels = {}
		self.subParsers = {
			# TEXT : self.parseLabel,
			# INS: self.parseInstruction,
			# NEWLINE : self.pop()
		}

		self.parseProgram()

	def parseDefine(self):
		self.tokens.expect(TEXT)

		if TEXT in self.consts:
			raise Exception('Redefinition of "%s"' % self.tokens.tokens[self.tokens.i])

		self.consts[TEXT] = []

		if self.tokens.accept(HASH):
			pass

		if self.tokens.accept(HEX):
			pass

		if self.tokens.accept(INT):
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
		if self.tokens.accept(NEWLINE):
			pass
		elif self.tokens.accept(KEYWORD):
			self.parseDefine()
			self.tokens.expect(NEWLINE)
		elif self.tokens.accept(TEXT):
			self.parseLabel()
			self.tokens.expect(NEWLINE)
		elif self.tokens.accept(INS):
			self.parseInstruction()
			self.tokens.expect(NEWLINE)
		else:
			raise Exception('Syntax error: "%s"' % self.tokens.tokens[self.tokens.i])

	def parseProgram(self):
		while not self.tokens.empty():
			self.parseLine()
			# self.tokens.expect(NEWLINE)

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
# preprocessor = Preprocessor(source)
# print(preprocessor.source)
tokenizer = Tokenizer(source)
# print(tokenizer.tokenStream)
lexer = Lexer(tokenizer.tokenStream)
print(lexer.tokens)
parser = Parser(lexer.tokens)
print(parser.consts)
# print(parser.instructions)
# print(len(parser.instructions))
# print()
# print(parser.opcodes)