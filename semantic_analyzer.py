from tokens import Tokens
from syntax_analyzer import make_syntax_analyzer
from peeker import Peeker
from tokenizer import make_tokenizer

# TODO merge parser and syntax analyzer
# TODO maybe move token into its own module as a general set of tokens for this stage of compilation
def analyze_semantics(syntax_analyzer):
	def parse_const_literal(literal):
		def is_hex(literal):
			return literal.startswith('$')

		def parse_hex(literal):
			return int(literal[1:], 16)

		def parse_dec(literal):
			return int(literal)

		return parse_hex(literal) if is_hex(literal) else parse_dec(literal)

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

			labels[name] = index

		tree, labels, ids = [], {}, {}

		for token in syntax_analyzer:
			token_type, *_ = token

			if token_type is Tokens.DEFINE:
				_, var_name, value = token
				add_define(ids, labels, var_name, value)
			elif token_type is Tokens.LABEL:
				_, name = token
				add_label(ids, labels, name, len(tree))
			else:
				tree.append(token)

		return (tree, ids, labels)

	def check_const_range(ids):
		for name, literal in ids.items():
			value = parse_const_literal(literal)

			if value > 0xFF:
				raise Exception('Value of {} ({}) is out of range'.format(name, value))

			ids[name] = value

	def sub_ids(tree, ids):
		def sub_defs(token_type, mne, name):
			return (token_type, mne, Tokens.CONSTANT, name)

		def sub_const(token_type, mne, literal):
			return (token_type, mne, Tokens.CONSTANT, parse_const_literal(literal))

		def sub_labels(token_type, mne, index):
			return (token_type, mne, Tokens.LABEL, index)

		processed_tree = []

		for item in tree:
			token_type, *_ = item

			if token_type is Tokens.NO_PARAM:
				processed_tree.append(item)
				continue

			_, mne, data_type, data = item

			if data_type is Tokens.IDENTIFIER and data in ids:
				processed_tree.append(sub_defs(token_type, mne, ids[data]))
			elif data_type is Tokens.CONSTANT:
				processed_tree.append(sub_const(token_type, mne, data))
			else:
				processed_tree.append(sub_labels(token_type, mne, labels[data]))

		return processed_tree

	tree, ids, labels = index_names(syntax_analyzer)
	check_const_range(ids)
	tree = sub_ids(tree, ids)

	return tree

if __name__ == '__main__':
	with open('test.asm') as file:
		print(analyze_semantics(make_syntax_analyzer(Peeker(make_tokenizer(file.read())))))
