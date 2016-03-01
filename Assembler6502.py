import re

class Token:
	def __init__(self, tokenType):
		self.__init__(tokenType, None)

	def __init__(self, tokenType, value):
		self.tokenType = tokenType
		self.value = value

	def __repr__(self):
		if self.value == None:
			return '%s' % self.tokenType

		return '%s: "%s"' % (self.tokenType, self.value)

class Tokenizer:
	def __init__(self, filename):
		self.tokens = {
			'KEY': r'define',
			'ID' : r'^[^\d\W]+[a-zA-Z0-9]+$',
			'IST': r'^[a-zA-Z]{3}$',
			'NBR': r'^\$?[0-9a-fA-F]+$',
			'COL': r':',
			'LIT': r'^#$',
			'CMA': r'^,$',
			'LB' : r'^\($',
			'RB' : r'^\)$',
			'REG': r'[xXyY]'
		}

		for key in self.tokens:
			pattern = self.tokens[key]
			self.tokens[key] = re.compile(pattern)

		self.priorities = ['KEY', 'REG', 'COL', 'RB', 'LB', 'CMA', 'LIT', 'IST', 'NBR', 'ID']

		self.file = open(filename, 'r')
		self.source = self.file.read()

		lines = re.split('[\n\r]', self.source)
		lines = [re.sub(';.+', '', line) for line in lines]
		lines = [line.strip() for line in lines]
		lines = [line for line in lines if len(line) > 0]
		self.lines = [self.tokenize(line) for line in lines]
		self.lines = [token for token in self.lines if token != None]

	def tokenize(self, line):
		splitLine = re.split('\s+|\b', line)
		tokenStr = []

		for token in splitLine:
			subtoken = ""
			for c in token:
				if "#.,():".find(c) != -1:
					if len(subtoken) > 0:
						tokenStr.append(subtoken)
					subtoken = ""
					tokenStr.append(c)
				else:
					subtoken += c

			if len(subtoken) > 0:
				tokenStr.append(subtoken)

		tokens = []

		for token in tokenStr:
			size = len(tokens)

			for tokenType in self.priorities:
				pattern = self.tokens[tokenType]

				if pattern.match(token):
					tokens.append(Token(tokenType, token))
					break;

			if size == len(tokens):
				print('"%s" is not a valid token. Line ditched' % token)

				return None;

		return tokens

class Parser:
	def __init__(self, lines):
		self.binary = []
		self.constants = {}
		self.labels = {}
		self.subParsers = {
			'KEY': self.parseKeyword,
			'ID' : self.parseID,
			'IST': self.parseInstruction,
			'NBR': self.parseHex,
			'COL': self.parseNone,
			'LIT': self.parseNone,
			'HEX': self.parseNone,
			'CMA': self.parseNone,
			'LB' : self.parseNone,
			'RB' : self.parseNone,
			'REG': self.parseNone
		}

		self.noOperand = 'No operand'
		self.immediate = 'Immediate'
		self.absolute = 'Absolute'
		self.relative = 'Relative'
		self.indirect = 'Indirect'
		self.zeroPage = 'Zero Page'
		self.zpxIndex = 'Zero Page X Indexed'
		self.zpyIndex = 'Zero Page Y Indexed'
		self.xIndirect = 'X Indirected'
		self.indirectY = 'Indirected Y'
		self.absX = 'Absolute X Indexed'
		self.absY = 'Absolute Y Indexed'

		self.opcodes = {
			('brk', self.noOperand)	: 0x00,	('ora', self.xIndirect): 0x01,                                                              ('ora', self.zeroPage): 0x05, ('asl', self.zeroPage): 0x06, ('php', self.noOperand): 0x08, ('ora', self.immediate): 0x09, ('asl', self.noOperand): 0x0A,                               ('ora', self.absolute): 0x0D, ('asl', self.absolute): 0x0E,
			('bpl', self.relative)	: 0x10,	('ora', self.indirectY): 0x11,                                                              ('ora', self.zpxIndex): 0x15, ('asl', self.zpxIndex): 0x16, ('clc', self.noOperand): 0x18, ('ora', self.absY)     : 0x19,                                                              ('ora', self.absX)    : 0x1D, ('asl', self.absX)    : 0x1E,
			('jsr', self.absolute)	: 0x20,	('and', self.xIndirect): 0x21,                                ('bit', self.zeroPage): 0x24, ('and', self.zeroPage): 0x25, ('rol', self.zeroPage): 0x26, ('plp', self.noOperand): 0x28, ('and', self.immediate): 0x29, ('rol', self.noOperand): 0x2A, ('bit', self.absolute): 0x2C, ('and', self.absolute): 0x2D, ('rol', self.absolute): 0x2E,
			('bmi', self.relative)	: 0x30,	('and', self.indirectY): 0x31,                                                              ('and', self.zpxIndex): 0x35, ('rol', self.zpxIndex): 0x36, ('sec', self.noOperand): 0x38, ('and', self.absY)     : 0x39,                                                              ('and', self.absX)    : 0x3D, ('rol', self.absX)    : 0x3E,
			('rti', self.noOperand)	: 0x40,	('eor', self.xIndirect): 0x41,                                                              ('eor', self.zeroPage): 0x45, ('lsr', self.zeroPage): 0x46, ('pha', self.noOperand): 0x48, ('eor', self.immediate): 0x49, ('lsr', self.noOperand): 0x4A, ('jmp', self.absolute): 0x4C, ('eor', self.absolute): 0x4D, ('lsr', self.absolute): 0x4E,
			('bvc', self.relative)	: 0x50,	('eor', self.indirectY): 0x51,                                                              ('eor', self.zpxIndex): 0x55, ('lsr', self.zpxIndex): 0x56, ('cli', self.noOperand): 0x58, ('eor', self.absY)     : 0x59,                                                              ('eor', self.absX)    : 0x5D, ('lsr', self.absX)    : 0x5E,
			('rts', self.noOperand)	: 0x60,	('adc', self.xIndirect): 0x61,                                                              ('adc', self.zeroPage): 0x65, ('ror', self.zeroPage): 0x66, ('pla', self.noOperand): 0x68, ('adc', self.immediate): 0x69, ('ror', self.noOperand): 0x6A, ('jmp', self.absolute): 0x6C, ('adc', self.absolute): 0x6D, ('ror', self.absolute): 0x6E,
			('bvs', self.relative)	: 0x70,	('adc', self.indirectY): 0x71,                                                              ('adc', self.zpxIndex): 0x75, ('ror', self.zpxIndex): 0x76, ('sei', self.noOperand): 0x78, ('adc', self.absY)     : 0x79,                                                              ('adc', self.absX)    : 0x7D, ('ror', self.absX)    : 0x7E,
			                                ('sta', self.xIndirect): 0x81,                                ('sty', self.zeroPage): 0x84, ('sta', self.zeroPage): 0x85, ('stx', self.zeroPage): 0x86, ('dey', self.noOperand): 0x88,                                ('txa', self.noOperand): 0x8A, ('sty', self.absolute): 0x8C, ('sta', self.absolute): 0x8D, ('stx', self.absolute): 0x8E,
			('bcc', self.relative)	: 0x90,	('sta', self.indirectY): 0x91,                                ('sty', self.zpxIndex): 0x94, ('sta', self.zpxIndex): 0x95, ('stx', self.zpxIndex): 0x96, ('tya', self.noOperand): 0x98, ('sta', self.absY)     : 0x99, ('txs', self.noOperand): 0x9A,                               ('sta', self.absX)    : 0x9D,
			('ldy', self.immediate)	: 0xA0,	('lda', self.xIndirect): 0xA1, ('ldx', self.immediate): 0xA2, ('ldy', self.zeroPage): 0xA4, ('lda', self.zeroPage): 0xA5, ('ldx', self.zeroPage): 0xA6, ('tay', self.noOperand): 0xA8, ('lda', self.immediate): 0xA9, ('tax', self.noOperand): 0xAA, ('ldy', self.absolute): 0xAC, ('lda', self.absolute): 0xAD, ('ldx', self.absolute): 0xAE,
			('bcs', self.relative)	: 0xB0,	('lda', self.indirectY): 0xB1,                                ('ldy', self.zpxIndex): 0xB4, ('lda', self.zpxIndex): 0xB5, ('ldx', self.zpxIndex): 0xB6, ('clv', self.noOperand): 0xB8, ('lda', self.absY)     : 0xB9, ('tsx', self.noOperand): 0xBA, ('ldy', self.absX)    : 0xBC, ('lda', self.absX)    : 0xBD, ('ldx', self.absX)    : 0xBE,
			('cpy', self.immediate)	: 0xC0,	('cmp', self.xIndirect): 0xC1,                                ('cpy', self.zeroPage): 0xC4, ('cmp', self.zeroPage): 0xC5, ('dec', self.zeroPage): 0xC6, ('iny', self.noOperand): 0xC8, ('cmp', self.immediate): 0xC9, ('dex', self.noOperand): 0xCA, ('cpy', self.absolute): 0xCC, ('cmp', self.absolute): 0xCD, ('dec', self.absolute): 0xCE,
			('bne', self.relative)	: 0xD0,	('cmp', self.indirectY): 0xD1,                                                              ('cmp', self.zpxIndex): 0xD5, ('dec', self.zpxIndex): 0xD6, ('cld', self.noOperand): 0xD8, ('cmp', self.absY)     : 0xD9,                                                              ('cmp', self.absX)    : 0xDD, ('dec', self.absX)    : 0xDE,
			('cpx', self.immediate)	: 0xE0,	('sbc', self.xIndirect): 0xE1,                                ('cpx', self.zeroPage): 0xE4, ('sbc', self.zeroPage): 0xE5, ('inc', self.zeroPage): 0xE6, ('inx', self.noOperand): 0xE8, ('sbc', self.immediate): 0xE9, ('nop', self.noOperand): 0xEA, ('cpx', self.absolute): 0xEC, ('sbc', self.absolute): 0xED, ('inc', self.absolute): 0xEE,
			('beq', self.relative)	: 0xF0,	('sbc', self.indirectY): 0xF1,                                                              ('sbc', self.zpxIndex): 0xF5, ('inc', self.zpxIndex): 0xF6, ('sed', self.noOperand): 0xF8, ('sbc', self.absY)     : 0xF9,                                                              ('sbc', self.absX)    : 0xFD, ('inc', self.absX)    : 0xFE
		}

		self.parseProgram(lines)

	def parseKeyword(self, tokens):
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
			return (self.noOperand, 0)

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
			# 	return (self.immediate, self.constants[operand.value])
			return (self.immediate, self.parseNumber(operand))

		operand = stream[0]

		if operand.tokenType == 'NBR':
			if len(operand.value) == 3:
				return (self.relative, self.parseNumber(operand))
			else:
				return (self.absolute, self.parseNumber(operand))

		if operand.tokenType == 'LB':
			print(stream)
			stream.pop(0)
			operand = stream[0]

			if stream[0] == 'CMA':
				return (self.xIndirect, self.parseNumber(operand))
			elif stream[0] == 'RB':
				return (self.indirectY, self.parseNumber(operand))
			else:
				stream.pop(0)
				return (self.indirect, self.parseNumber(operand))

	def parseInstruction(self, tokens):
		print(tokens)
		instruction = tokens[0]
		tokens.pop(0)

		# print(instruction)

		mode = self.parseOperand(tokens)
		key = (instruction.value, mode[0])

		if not (key in self.opcodes) and mode[0] == self.relative:
			key = (key[0], self.absolute)

		if not (key in self.opcodes) and mode[0] == self.absolute:
			key = (key[0], self.relative)

		print(key)

		print(self.opcodes[key])

	def parseHex(self, token):
		return int(token.value, 16)

	def parseProgram(self, lines):
		for line in lines:
			self.parseLine(line)

	def parseNone(self, lines):
		pass

	def parseLine(self, line):
		self.subParsers[line[0].tokenType](line)

tokenizer = Tokenizer('test.asm')
# print(tokenizer.lines)
# print()
parser = Parser(tokenizer.lines)
# print(parser.constants)
# print()
# print(parser.labels)
# print()
# print(parser.opcodes)