from enum import Enum
from peeker import Peeker
from tokenizer import Tokens as lexer
from tokenizer import make_tokenizer

class Tokens(Enum):
	DEFINE, IDENTIFIER, CONSTANT, IMMEDIATE, NO_PARAM, ONE_PARAM, X_INDEX, Y_INDEX, LABEL, X_INDIRECT, INDIRECT_Y = range(11)

	def __repr__(self):
		return self.name

def make_syntax_analyzer(peekable):
	def accept(token_type):
		try:
			ttype, _ = peekable.peek()

			return ttype is token_type
		except StopIteration:
			return False

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
		def operand():
			return (Tokens.CONSTANT, *expect(lexer.CONSTANT)[1:]) if accept(lexer.CONSTANT) else (Tokens.IDENTIFIER, *expect(lexer.IDENTIFIER)[1:])

		def immediate(mne):
			expect(lexer.HASH)

			return (Tokens.IMMEDIATE, mne, *operand())

		def indirects(mne):
			def indirect_y():
				expect(lexer.Y_INDEX)

				return (Tokens.INDIRECT_Y, mne, *param)

			expect(lexer.LEFT_BRACKET)
			param = operand()

			if accept(lexer.RIGHT_BRACKET):
				expect(lexer.RIGHT_BRACKET)

				if accept(lexer.Y_INDEX):
					return indirect_y()

				return (Tokens.INDIRECT, mne, *param)

			expect(lexer.X_INDEX)
			expect(lexer.RIGHT_BRACKET)

			return (Tokens.X_INDIRECT, mne, *param)

		def direct(mne):
			# TODO maybe split up param so that it's unpacked in the if statements?
			def x_index(param):
				expect(lexer.X_INDEX)

				return (Tokens.X_INDEX, mne, *param)

			def y_index(param):
				expect(lexer.Y_INDEX)

				return (Tokens.Y_INDEX, mne, *param)

			param = operand()

			if accept(lexer.X_INDEX):
				return x_index(param)
			elif accept(lexer.Y_INDEX):
				return y_index(param)

			return (Tokens.ONE_PARAM, mne, *param)

		_, mne = expect(lexer.MNEMONIC)

		if accept(lexer.HASH):
			return immediate(mne)
		elif accept(lexer.LEFT_BRACKET):
			return indirects(mne)
		elif accept(lexer.CONSTANT) or accept(lexer.IDENTIFIER):
			return direct(mne)

		return (Tokens.NO_PARAM, mne)

	def label():
		_, name = expect(lexer.IDENTIFIER)
		expect(lexer.COLON)

		return (Tokens.LABEL, name)

	while True:
		token_type, value = peekable.peek()

		if token_type is lexer.DEFINE:
			yield define()
		elif token_type is lexer.MNEMONIC:
			yield instruction()
		elif token_type is lexer.IDENTIFIER:
			yield label()
		elif token_type is lexer.NEWLINE:
			expect(lexer.NEWLINE)
		else:
			raise Exception('Syntax error')

if __name__ == '__main__':
	with open('test.asm') as file:
		source = file.read()
		syntax_analyzer = make_syntax_analyzer(Peeker(make_tokenizer(source)))

		print([x for x in syntax_analyzer])
