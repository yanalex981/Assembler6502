from tokens import Tokens
from peeker import Peeker

class Parser:
	def __init__(self, stream):
		self.__instr_counter = 0
		self.__stream = stream
		self.__ids = dict()
		self.__labels = dict()

	def get(self, name):
		if name in self.__labels:
			return self.__labels[name]

		if name in self.__ids:
			return self.__ids[name]

		raise Exception('{} is not found'.format(name))

	@property
	def ids(self):
		return self.__ids

	@property
	def labels(self):
		return self.__labels

	def index_name(self, token):
		def add_define(var_name, value):
			if var_name in self.__ids:
				raise Exception('The constant "{}" is already a constant'.format(var_name))
			elif var_name in self.__labels:
				raise Exception('The constant "{}" is already a label'.format(var_name))

			self.__ids[var_name] = value

		def add_label(name, index):
			if name in self.__ids:
				raise Exception('The label "{}" is already a constant'.format(name))
			elif name in self.__labels:
				raise Exception('The label "{}" is already a label'.format(name))

			self.__labels[name] = index

		if token_type is Tokens.DEFINE:
			_, var_name, value = token
			add_define(ids, labels, var_name, value)
		elif token_type is Tokens.LABEL:
			_, name = token
			add_label(ids, labels, name, len(tree))
		else:
			tree.append(token)

		return (tree, ids, labels)

	def __next__(self):
		while True:
			token = next(self.__stream)
			token_type, *_ = token

			if token_type not in {Tokens.DEFINE, Tokens.LABEL}:
				self.__instr_counter += 1

				return token

			if token_type is Tokens.DEFINE:
				_, name, value = token
				self.__ids[name] = value
			elif token_type is Tokens.LABEL:
				_, name = token
				self.__labels[name] = self.__instr_counter

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
