from enum import Enum
import re

class Tokens(Enum):
	MNEMONIC, DEFINE, IDENTIFIER, CONSTANT, SPACES, COLON, HASH, LEFT_BRACKET, RIGHT_BRACKET, X_INDEX, Y_INDEX, NEWLINE, COMMENT, BAD_TOKEN = range(14)

	def __repr__(self):
		return self.name

def make_matcher(pattern, token):
	matcher = re.compile(pattern)

	def match(src, pos):
		match = matcher.match(src, pos)

		return None if match is None else (token, match.group())

	return match

def make_tokenizer(src):
	mnemonic = {'ldx', 'lsr', 'rti', 'sta', 'bcs', 'brk', 'sed', 'sec', 'beq', 'cpy', 'pla', 'and', 'tax', 'sty', 'dey', 'inx', 'rts', 'sei', 'bne', 'bvc', 'eor', 'asl', 'cmp', 'txs', 'txa', 'jmp', 'ror', 'nop', 'stx', 'inc', 'iny', 'bvs', 'adc', 'cld', 'pha', 'tya', 'ora', 'plp', 'jsr', 'bit', 'lda', 'bmi', 'tsx', 'rol', 'cpx', 'php', 'dex', 'bpl', 'clv', 'clc', 'dec', 'bcc', 'ldy', 'tay', 'sbc', 'cli'}
	instruction_pattern = '\\b({})\\b'.format('|'.join(mnemonic))

	rules = (
		make_matcher(r'\r\n|\r|\n'            , Tokens.NEWLINE),
		make_matcher(instruction_pattern      , Tokens.MNEMONIC),
		make_matcher(r'\bdefine\b'            , Tokens.DEFINE),
		make_matcher(r'[_a-zA-Z][_a-zA-Z0-9]*', Tokens.IDENTIFIER),
		make_matcher(r'[ \t]+'                , Tokens.SPACES),
		make_matcher(r'#'                     , Tokens.HASH),
		make_matcher(r'(\d+|\$[0-9a-fA-F]+)\b', Tokens.CONSTANT),
		make_matcher(r',\s*[Xx]\b'            , Tokens.X_INDEX),
		make_matcher(r',\s*[Yy]\b'            , Tokens.Y_INDEX),
		make_matcher(r':'                     , Tokens.COLON),
		make_matcher(r'\('                    , Tokens.LEFT_BRACKET),
		make_matcher(r'\)'                    , Tokens.RIGHT_BRACKET),
		make_matcher(r';.*'                   , Tokens.COMMENT),
		make_matcher(r'.+'                    , Tokens.BAD_TOKEN)
	)

	ignore = {Tokens.COMMENT, Tokens.SPACES}

	pos, line = 0, 1

	while pos < len(src):
		for matcher in rules:
			match = matcher(src, pos)

			if match is None:
				continue

			pos += len(match[1])
			token, _ = match

			line += 1 if token == Tokens.NEWLINE else 0

			if token not in ignore:
				yield match

			break
		else:
			raise Exception('Error tokenizing at {}:{}: {}'.format(line, pos, src)) # pos is wrong

if __name__ == '__main__':
	file = open('test.asm')
	source = file.read()

	tokenizer = make_tokenizer(source)
	print([x for x in tokenizer])
