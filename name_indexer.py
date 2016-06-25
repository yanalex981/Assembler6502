from enum import Enum
from syntax_analyzer import Tokens as sa
from syntax_analyzer import make_syntax_analyzer
from peeker import Peeker
from tokenizer import make_tokenizer

def index_names(syntax_analyzer):
	def add_define(ids, labels, var_name, value):
		if var_name in ids:
			raise Exception('The constant "{}" is already a constant'.format(var_name))
		elif var_name in labels:
			raise Exception('The constant "{}" is already a label'.format(var_name))

		ids[var_name] = value

	def add_label(ids, labels, name, index):
		if name in ids:
			raise Exception('The label "{}" is already a constant'.format(name))
		elif name in labels:
			raise Exception('The label "{}" is already a label'.format(name))

		# do counter
		labels[name] = index

	tokens = []
	labels = {}
	ids = {}

	for token in syntax_analyzer:
		token_type, *_ = token

		if token_type is sa.DEFINE:
			_, var_name, value = token
			add_define(ids, labels, var_name, value)
		elif token_type is sa.LABEL:
			_, name = token
			add_label(ids, labels, name, len(tokens))
		else:
			tokens.append(token)

	return (tokens, ids, labels)

if __name__ == '__main__':
	with open('test5.asm') as file:
		source = file.read()
		indices = index_names(make_syntax_analyzer(Peeker(make_tokenizer(source))))

		tokens, ids, labels = indices
		print(tokens)
		print()
		print(ids)
		print()
		print(labels)
