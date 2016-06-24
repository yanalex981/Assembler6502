from enum import Enum
from tokenizer import Tokens as lexer
from tokenizer import tokenize

class Tokens(Enum):
	MNEMONIC, DEFINE, IDENTIFIER, CONSTANT,  = range(14)

class Peeker:
	def __init__(self, stream):
		self.__current = next(stream)
		self.__stream = stream

	def peek(self):
		if self.__current is None:
			# TODO get rid of this side effect by copying the generator on creation?
			self.__current = next(self.__stream)

		return self.__current

	def __next__(self):
		current = self.peek()
		self.__current = None

		return current

	def __iter__(self):
		return self

def make_syntax_analyzer(peekable):
	def accept(token_type):
		ttype, _ = peekable.peek()

		return ttype is token_type

	def expect(token_type):
		if not accept(token_type):
			raise Exception('Unexpected token encountered')

		return next(peekable)

	def define():
		expect(lexer.DEFINE)
		_, name = expect(lexer.IDENTIFIER)
		_, value = expect(lexer.CONSTANT)

		return (Tokens.DEFINE, name, value)

	def instruction():
		expect(lexer.MNEMONIC)

		if accept(lexer.HASH):
			return immediate()
		elif accept(lexer.LEFT_BRACKET):
			return indirects()
		elif accept(lexer.CONSTANT) or accept(lexer.IDENTIFIER):
			operand = operand()

			if accept(lexer.X_INDEX):
				expect(lexer.X_INDEX)
				emit(Token(ABSX))
				emit(operand)

				return
			elif accept(lexer.Y_INDEX):
				stream.expect(lexer.Y_INDEX)
				emit(Token(ABSY))
				emit(operand)

				return
			
			emit(Token(UNARY))
			emit(operand)

		emit(Token(NULL))
		return

	def label():
		name = expect(lexer.IDENTIFIER)
		expect(lexer.COLON)

	while True:
		token_type, value = peekable.peek()

		if token_type == lexer.DEFINE:
			yield define()
		elif token_type is lexer.MNEMONIC:
			yield instruction()
		elif token_type is lexer.IDENTIFIER:
			yield label()
		else:
			raise Exception('Syntax error')

with open('defines.asm') as file:
	source = file.read()
	tokenizer = tokenize(source)
	syntax_analyzer = make_syntax_analyzer(Peeker(tokenizer))

	print([x for x in syntax_analyzer])

"""
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
				if self.stream.accept(lexer.DEFINE):
					self.define()
				elif self.stream.accept(lexer.MNEMONIC):
					self.instruction()
				elif self.stream.accept(lexer.IDENTIFIER):
					self.label()
				else:
					print(self.stream)
					raise Exception('Syntax error')

		# print(self.results)

	def emit(self, token):
		self.results.append(token)

	def define(self):
		self.stream.expect(lexer.DEFINE)
		name = self.stream.expect(lexer.IDENTIFIER).get_value()
		value = self.stream.expect(lexer.CONSTANT).get_value()
		self.emit(Token(lexer.DEFINE, (name, value)))

	def operand(self):
		return self.stream.expect(lexer.CONSTANT) if self.stream.accept(lexer.CONSTANT) else self.stream.expect(lexer.IDENTIFIER)

	def indirects(self):
		self.stream.expect(lexer.LEFT_BRACKET)
		param = self.operand()

		if self.stream.accept(lexer.RIGHT_BRACKET):
			self.stream.expect(lexer.RIGHT_BRACKET)

			if self.stream.accept(lexer.Y_INDEX):
				self.stream.expect(lexer.Y_INDEX)
				self.emit(Token(INDY))
			else:
				self.emit(Token(INDR))
		else:
			self.stream.expect(lexer.X_INDEX)
			self.stream.expect(lexer.RIGHT_BRACKET)
			self.emit(Token(XIND))

		self.emit(param)

	def immediate(self):
		self.stream.expect(lexer.HASH)
		param = self.operand()
		self.emit(Token(IMED))
		self.emit(param)

	def instruction(self):
		self.emit(self.stream.expect(lexer.MNEMONIC))

		self.ins_counter += 1

		if self.stream.accept(lexer.HASH):
			self.immediate()
			return
		elif self.stream.accept(lexer.LEFT_BRACKET):
			self.indirects()
			return
		elif self.stream.accept(lexer.CONSTANT) or self.stream.accept(lexer.IDENTIFIER):
			operand = self.operand()

			if self.stream.accept(lexer.X_INDEX):
				self.stream.expect(lexer.X_INDEX)
				self.emit(Token(ABSX))
				self.emit(operand)
				return
			elif self.stream.accept(lexer.Y_INDEX):
				self.stream.expect(lexer.Y_INDEX)
				self.emit(Token(ABSY))
				self.emit(operand)
				return
			
			self.emit(Token(UNARY))
			self.emit(operand)
			return

		self.emit(Token(NULL))
		return

	def label(self):
		name = self.stream.expect(lexer.IDENTIFIER).get_value()
		self.stream.expect(lexer.COLON)

		self.labels[name] = self.ins_counter
"""