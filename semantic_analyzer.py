from tokens import Tokens
from asm_parser import Parser

# TODO merge parser and syntax analyzer
# TODO maybe move token into its own module as a general set of tokens for this stage of compilation
def analyze_semantics(parser):
	def parse_const_literal(value):
		return int(value[1:], 16) if value.startswith('$') else int(value)

	def check_const_range(instr):
		mne_type, mne, param_type, value = instr

		if param_type is Tokens.CONSTANT and value > 0xFF:
			raise Exception('Value of {} ({}) is out of range'.format(name, value))

		return instr

	def sub_params(instr):
		mne_type, mne, param_type, value = instr

		if mne_type in {Tokens.NO_PARAM}:
			return (mne_type, mne, param_type, value)

		if param_type is Tokens.IDENTIFIER:
			if value in parser.ids:
				return (mne_type, mne, Tokens.CONSTANT, parse_const_literal(parser.ids[value]))

			return (mne_type, mne, Tokens.LABEL, parser.labels[value])

		return (mne_type, mne, Tokens.CONSTANT, parse_const_literal(value))

	return [check_const_range(sub_params(instr)) for instr in parser]

if __name__ == '__main__':
	from tokenizer import make_tokenizer
	from syntax_analyzer import make_syntax_analyzer
	from peeker import Peeker

	with open('test.asm') as file:
		# parser.Parser(None)
		analyzer = analyze_semantics(Parser(make_syntax_analyzer(Peeker(make_tokenizer(file.read())))))
		print(analyzer)
