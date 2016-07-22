from tokens import Tokens
from peeker import Peeker

class Parser:
	def __init__(self, stream):
		self.__ids = {}
		self.__labels = {}

		def index_labels(stream):
			counter, filtered_src = 0, []

			for line in stream:
				token_type, *_ = line

				if token_type is Tokens.LABEL:
					_, name = line
					if name in self.__labels:
						raise Exception('Label "{}" is already defined'.format(name))
					self.__labels[name] = counter
				elif token_type is not Tokens.DEFINE:
					counter += 1
					filtered_src.append(line)
				else:
					filtered_src.append(line)

			return (x for x in filtered_src)

		self.__stream = index_labels(stream)

	@property
	def ids(self):
		return self.__ids

	@property
	def labels(self):
		return self.__labels

	def __next__(self):
		def add_define(name, value):
			if name in self.__ids:
				raise Exception('Constant "{}" is already defined'.format(name))
			elif name in self.__labels:
				raise Exception('Constant "{}" is already a label'.format(name))

			self.__ids[name] = value

		while True:
			token = next(self.__stream)
			token_type, *_ = token

			if token_type not in {Tokens.DEFINE, Tokens.LABEL}:
				return token

			if token_type is Tokens.DEFINE:
				_, name, value = token
				add_define(name, value)

	def __iter__(self):
		return self

if __name__ == '__main__':
	from syntax_analyzer import make_syntax_analyzer
	from tokenizer import make_tokenizer

	with open('test.asm') as file:
		parser = Parser(make_syntax_analyzer(Peeker(make_tokenizer(file.read()))))

		print([x for x in parser])

		print(parser.ids)
		print(parser.labels)
