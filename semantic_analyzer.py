from tokens import Tokens
from asm_parser import Parser

# TODO merge parser and syntax analyzer
# TODO maybe move token into its own module as a general set of tokens for this stage of compilation
def analyze_semantics(parser):
	def parse_const_literal(literal):
		def parse_hex(literal):
			return int(literal[1:], 16)

		def parse_dec(literal):
			return int(literal)

		return parse_hex(literal) if literal.startswith('$') else parse_dec(literal)

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

	# check_const_range(ids)
	# tree = sub_ids(tree, ids)

	# sub params
	# disambiguate addressing modes
	# check param range

	def sub_params(instr):
		mne_type, mne, param_type, value = instr

		if mne_type in {Tokens.NO_PARAM}:
			return (mne_type, mne, param_type, value)

		if param_type is Tokens.IDENTIFIER:
			return (mne_type, mne, Tokens.LABEL, parser.get(value))

		return (mne_type, mne, Tokens.CONSTANT, parser.get(value))

	for instr in parser:
		yield sub_params(instr)

if __name__ == '__main__':
	from tokenizer import make_tokenizer
	from syntax_analyzer import make_syntax_analyzer
	from peeker import Peeker

	with open('test.asm') as file:
		# parser.Parser(None)
		analyzer = analyze_semantics(Parser(make_syntax_analyzer(Peeker(make_tokenizer(file.read())))))
		print([x for x in analyzer])
