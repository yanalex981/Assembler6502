import sys

from peeker import Peeker
from tokens import Tokens
from asm_parser import Parser
from tokenizer import make_tokenizer
from semantic_analyzer import analyze_semantics
from syntax_analyzer import make_syntax_analyzer
from code_generator import generate_code

if __name__ == '__main__':
	_, input_file_name, output_file_name, *_ = sys.argv

	start_address = 0
	if len(sys.argv) > 3:
		start_address = int(sys.argv[3])

	with open(input_file_name, 'r') as input_file:
		print('File opened')
		source = input_file.read()
		code = generate_code(analyze_semantics(Parser(make_syntax_analyzer(Peeker(make_tokenizer(source))))), start_address)
		with open(output_file_name, 'wb') as output_file:
			output_file.write(bytes(code))
			print('File written')
