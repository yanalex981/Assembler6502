from tokens import Tokens
from peeker import Peeker
from tokenizer import make_tokenizer

def make_syntax_analyzer(peekable):
	def accept(token_type):
		try:
			ttype, _ = peekable.peek()

			return ttype is token_type
		except StopIteration:
			return False

	def expect(token_type):
		ttype = accept(token_type)

		if not ttype:
			raise Exception('Expected {}, but encountered {}'.format(token_type, ttype))

		return next(peekable)

	def define():
		expect(Tokens.DEFINE)
		_, name = expect(Tokens.IDENTIFIER)
		_, value = expect(Tokens.CONSTANT)

		return (Tokens.DEFINE, name, value)

	def instruction():
		def operand():
			return (Tokens.CONSTANT, *expect(Tokens.CONSTANT)[1:]) if accept(Tokens.CONSTANT) else (Tokens.IDENTIFIER, *expect(Tokens.IDENTIFIER)[1:])

		def immediate(mne):
			expect(Tokens.HASH)

			return (Tokens.IMMEDIATE, mne, *operand())

		def indirects(mne):
			def indirect_y():
				expect(Tokens.Y_INDEX)

				return (Tokens.INDIRECT_Y, mne, *param)

			expect(Tokens.LEFT_BRACKET)
			param = operand()

			if accept(Tokens.RIGHT_BRACKET):
				expect(Tokens.RIGHT_BRACKET)

				if accept(Tokens.Y_INDEX):
					return indirect_y()

				return (Tokens.INDIRECT, mne, *param)

			expect(Tokens.X_INDEX)
			expect(Tokens.RIGHT_BRACKET)

			return (Tokens.X_INDIRECT, mne, *param)

		def direct(mne):
			# TODO maybe split up param so that it's unpacked in the if statements?
			def x_index(param):
				expect(Tokens.X_INDEX)

				return (Tokens.X_INDEX, mne, *param)

			def y_index(param):
				expect(Tokens.Y_INDEX)

				return (Tokens.Y_INDEX, mne, *param)

			param = operand()

			if accept(Tokens.X_INDEX):
				return x_index(param)
			elif accept(Tokens.Y_INDEX):
				return y_index(param)

			return (Tokens.ONE_PARAM, mne, *param)

		_, mne = expect(Tokens.MNEMONIC)

		if accept(Tokens.HASH):
			return immediate(mne)
		elif accept(Tokens.LEFT_BRACKET):
			return indirects(mne)
		elif accept(Tokens.CONSTANT) or accept(Tokens.IDENTIFIER):
			return direct(mne)

		return (Tokens.NO_PARAM, mne)

	def label():
		_, name = expect(Tokens.IDENTIFIER)
		expect(Tokens.COLON)

		return (Tokens.LABEL, name)

	while True:
		token_type, value = peekable.peek()

		if token_type is Tokens.DEFINE:
			yield define()
		elif token_type is Tokens.MNEMONIC:
			yield instruction()
		elif token_type is Tokens.IDENTIFIER:
			yield label()
		elif token_type is Tokens.NEWLINE:
			expect(Tokens.NEWLINE)
		else:
			raise Exception('Syntax error')

if __name__ == '__main__':
	with open('test.asm') as file:
		source = file.read()
		syntax_analyzer = make_syntax_analyzer(Peeker(make_tokenizer(source)))

		print([x for x in syntax_analyzer])
