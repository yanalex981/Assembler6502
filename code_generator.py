from peeker import Peeker
from tokens import Tokens
from asm_parser import Parser
from tokenizer import make_tokenizer
from semantic_analyzer import analyze_semantics
from syntax_analyzer import make_syntax_analyzer

def generate_code(sem_output, start_address=0x600):
	opcodes = {
		('brk', Tokens.NO_PARAM) : 0x00, ('ora', Tokens.X_INDIRECT): 0x01,                                                                 ('ora', Tokens.ZERO)  : 0x05, ('asl', Tokens.ZERO)  : 0x06, ('php', Tokens.NO_PARAM): 0x08, ('ora', Tokens.IMMEDIATE) : 0x09, ('asl', Tokens.NO_PARAM): 0x0A,                                   ('ora', Tokens.ABSOLUTE)  : 0x0D, ('asl', Tokens.ABSOLUTE)  : 0x0E,
		('bpl', Tokens.RELATIVE) : 0x10, ('ora', Tokens.INDIRECT_Y): 0x11,                                                                 ('ora', Tokens.ZERO_X): 0x15, ('asl', Tokens.ZERO_X): 0x16, ('clc', Tokens.NO_PARAM): 0x18, ('ora', Tokens.ABSOLUTE_Y): 0x19,                                                                   ('ora', Tokens.ABSOLUTE_X): 0x1D, ('asl', Tokens.ABSOLUTE_X): 0x1E,
		('jsr', Tokens.ABSOLUTE) : 0x20, ('and', Tokens.X_INDIRECT): 0x21,                                   ('bit', Tokens.ZERO)  : 0x24, ('and', Tokens.ZERO)  : 0x25, ('rol', Tokens.ZERO)  : 0x26, ('plp', Tokens.NO_PARAM): 0x28, ('and', Tokens.IMMEDIATE) : 0x29, ('rol', Tokens.NO_PARAM): 0x2A, ('bit', Tokens.ABSOLUTE)  : 0x2C, ('and', Tokens.ABSOLUTE)  : 0x2D, ('rol', Tokens.ABSOLUTE)  : 0x2E,
		('bmi', Tokens.RELATIVE) : 0x30, ('and', Tokens.INDIRECT_Y): 0x31,                                                                 ('and', Tokens.ZERO_X): 0x35, ('rol', Tokens.ZERO_X): 0x36, ('sec', Tokens.NO_PARAM): 0x38, ('and', Tokens.ABSOLUTE_Y): 0x39,                                                                   ('and', Tokens.ABSOLUTE_X): 0x3D, ('rol', Tokens.ABSOLUTE_X): 0x3E,
		('rti', Tokens.NO_PARAM) : 0x40, ('eor', Tokens.X_INDIRECT): 0x41,                                                                 ('eor', Tokens.ZERO)  : 0x45, ('lsr', Tokens.ZERO)  : 0x46, ('pha', Tokens.NO_PARAM): 0x48, ('eor', Tokens.IMMEDIATE) : 0x49, ('lsr', Tokens.NO_PARAM): 0x4A, ('jmp', Tokens.ABSOLUTE)  : 0x4C, ('eor', Tokens.ABSOLUTE)  : 0x4D, ('lsr', Tokens.ABSOLUTE)  : 0x4E,
		('bvc', Tokens.RELATIVE) : 0x50, ('eor', Tokens.INDIRECT_Y): 0x51,                                                                 ('eor', Tokens.ZERO_X): 0x55, ('lsr', Tokens.ZERO_X): 0x56, ('cli', Tokens.NO_PARAM): 0x58, ('eor', Tokens.ABSOLUTE_Y): 0x59,                                                                   ('eor', Tokens.ABSOLUTE_X): 0x5D, ('lsr', Tokens.ABSOLUTE_X): 0x5E,
		('rts', Tokens.NO_PARAM) : 0x60, ('adc', Tokens.X_INDIRECT): 0x61,                                                                 ('adc', Tokens.ZERO)  : 0x65, ('ror', Tokens.ZERO)  : 0x66, ('pla', Tokens.NO_PARAM): 0x68, ('adc', Tokens.IMMEDIATE) : 0x69, ('ror', Tokens.NO_PARAM): 0x6A, ('jmp', Tokens.INDIRECT)  : 0x6C, ('adc', Tokens.ABSOLUTE)  : 0x6D, ('ror', Tokens.ABSOLUTE)  : 0x6E,
		('bvs', Tokens.RELATIVE) : 0x70, ('adc', Tokens.INDIRECT_Y): 0x71,                                                                 ('adc', Tokens.ZERO_X): 0x75, ('ror', Tokens.ZERO_X): 0x76, ('sei', Tokens.NO_PARAM): 0x78, ('adc', Tokens.ABSOLUTE_Y): 0x79,                                                                   ('adc', Tokens.ABSOLUTE_X): 0x7D, ('ror', Tokens.ABSOLUTE_X): 0x7E,
		                                 ('sta', Tokens.X_INDIRECT): 0x81,                                   ('sty', Tokens.ZERO)  : 0x84, ('sta', Tokens.ZERO)  : 0x85, ('stx', Tokens.ZERO)  : 0x86, ('dey', Tokens.NO_PARAM): 0x88,                                   ('txa', Tokens.NO_PARAM): 0x8A, ('sty', Tokens.ABSOLUTE)  : 0x8C, ('sta', Tokens.ABSOLUTE)  : 0x8D, ('stx', Tokens.ABSOLUTE)  : 0x8E,
		('bcc', Tokens.RELATIVE) : 0x90, ('sta', Tokens.INDIRECT_Y): 0x91,                                   ('sty', Tokens.ZERO_X): 0x94, ('sta', Tokens.ZERO_X): 0x95, ('stx', Tokens.ZERO_Y): 0x96, ('tya', Tokens.NO_PARAM): 0x98, ('sta', Tokens.ABSOLUTE_Y): 0x99, ('txs', Tokens.NO_PARAM): 0x9A,                                   ('sta', Tokens.ABSOLUTE_X): 0x9D,
		('ldy', Tokens.IMMEDIATE): 0xA0, ('lda', Tokens.X_INDIRECT): 0xA1, ('ldx', Tokens.IMMEDIATE) : 0xA2, ('ldy', Tokens.ZERO)  : 0xA4, ('lda', Tokens.ZERO)  : 0xA5, ('ldx', Tokens.ZERO)  : 0xA6, ('tay', Tokens.NO_PARAM): 0xA8, ('lda', Tokens.IMMEDIATE) : 0xA9, ('tax', Tokens.NO_PARAM): 0xAA, ('ldy', Tokens.ABSOLUTE)  : 0xAC, ('lda', Tokens.ABSOLUTE)  : 0xAD, ('ldx', Tokens.ABSOLUTE)  : 0xAE,
		('bcs', Tokens.RELATIVE) : 0xB0, ('lda', Tokens.INDIRECT_Y): 0xB1,                                   ('ldy', Tokens.ZERO_X): 0xB4, ('lda', Tokens.ZERO_X): 0xB5, ('ldx', Tokens.ZERO_Y): 0xB6, ('clv', Tokens.NO_PARAM): 0xB8, ('lda', Tokens.ABSOLUTE_Y): 0xB9, ('tsx', Tokens.NO_PARAM): 0xBA, ('ldy', Tokens.ABSOLUTE_X): 0xBC, ('lda', Tokens.ABSOLUTE_X): 0xBD, ('ldx', Tokens.ABSOLUTE_X): 0xBE,
		('cpy', Tokens.IMMEDIATE): 0xC0, ('cmp', Tokens.X_INDIRECT): 0xC1,                                   ('cpy', Tokens.ZERO)  : 0xC4, ('cmp', Tokens.ZERO)  : 0xC5, ('dec', Tokens.ZERO)  : 0xC6, ('iny', Tokens.NO_PARAM): 0xC8, ('cmp', Tokens.IMMEDIATE) : 0xC9, ('dex', Tokens.NO_PARAM): 0xCA, ('cpy', Tokens.ABSOLUTE)  : 0xCC, ('cmp', Tokens.ABSOLUTE)  : 0xCD, ('dec', Tokens.ABSOLUTE)  : 0xCE,
		('bne', Tokens.RELATIVE) : 0xD0, ('cmp', Tokens.INDIRECT_Y): 0xD1,                                                                 ('cmp', Tokens.ZERO_X): 0xD5, ('dec', Tokens.ZERO_X): 0xD6, ('cld', Tokens.NO_PARAM): 0xD8, ('cmp', Tokens.ABSOLUTE_Y): 0xD9,                                                                   ('cmp', Tokens.ABSOLUTE_X): 0xDD, ('dec', Tokens.ABSOLUTE_X): 0xDE,
		('cpx', Tokens.IMMEDIATE): 0xE0, ('sbc', Tokens.X_INDIRECT): 0xE1,                                   ('cpx', Tokens.ZERO)  : 0xE4, ('sbc', Tokens.ZERO)  : 0xE5, ('inc', Tokens.ZERO)  : 0xE6, ('inx', Tokens.NO_PARAM): 0xE8, ('sbc', Tokens.IMMEDIATE) : 0xE9, ('nop', Tokens.NO_PARAM): 0xEA, ('cpx', Tokens.ABSOLUTE)  : 0xEC, ('sbc', Tokens.ABSOLUTE)  : 0xED, ('inc', Tokens.ABSOLUTE)  : 0xEE,
		('beq', Tokens.RELATIVE) : 0xF0, ('sbc', Tokens.INDIRECT_Y): 0xF1,                                                                 ('sbc', Tokens.ZERO_X): 0xF5, ('inc', Tokens.ZERO_X): 0xF6, ('sed', Tokens.NO_PARAM): 0xF8, ('sbc', Tokens.ABSOLUTE_Y): 0xF9,                                                                   ('sbc', Tokens.ABSOLUTE_X): 0xFD, ('inc', Tokens.ABSOLUTE_X): 0xFE
	}

	def deduce_addressing_mode(instr):
		def deduce(mode, mne, data_type, value):
			if mode is Tokens.ONE_PARAM:
				if (mne, Tokens.RELATIVE) in opcodes:
					return (Tokens.RELATIVE, mne, data_type, value)
				elif (mne, Tokens.ZERO) in opcodes and value < 256:
					return (Tokens.ZERO, mne, data_type, value)
				elif (mne, Tokens.ABSOLUTE) in opcodes:
					return (Tokens.ABSOLUTE, mne, data_type, value)
			elif mode is Tokens.X_INDEX:
				if (mne, Tokens.ZERO_X) in opcodes and value < 256:
					return (Tokens.ZERO_X, mne, data_type, value)
				elif (mne, Tokens.ABSOLUTE_X) in opcodes:
					return (Tokens.ABSOLUTE_X, mne, data_type, value)
			elif mode is Tokens.Y_INDEX:
				if (mne, Tokens.ZERO_Y) in opcodes and value < 256:
					return (Tokens.ZERO_Y, mne, data_type, value)
				elif (mne, Tokens.ABSOLUTE_Y) in opcodes:
					return (Tokens.ABSOLUTE_Y, mne, data_type, value)

			raise Exception('Cannot deduce addressing mode for "{} {} {}:{}"'.format(mne, mode, data_type, value))

		mode, mne, *_ = instr

		if mode in {Tokens.ONE_PARAM, Tokens.X_INDEX, Tokens.Y_INDEX}:
			return deduce(*instr)
		else:
			return instr

	def compute_size(instr):
		mode, mne, data_type, value = instr

		if mode is Tokens.NO_PARAM:
			return 1

		if mode in {Tokens.IMMEDIATE, Tokens.X_INDIRECT, Tokens.INDIRECT_Y, Tokens.RELATIVE, Tokens.ZERO, Tokens.ZERO_X, Tokens.ZERO_Y}:
			return 2
		else:
			return 3

	def compute_address(size_table):
		address = start_address
		address_table = []

		for size in size_table:
			address_table.append(address)
			address += size

		return address_table

	def sub_params(addr, instr, address_table):
		mode, mne, data_type, value = instr
		
		if mode is Tokens.NO_PARAM:
			return (mode, mne, None)

		if data_type is Tokens.LABEL:
			return (mode, mne, address_table[value])
		
		if data_type is Tokens.CONSTANT:
			return (mode, mne, value)

	def patch_relative_param(addr, instr):
		mode, mne, value = instr

		if mode is not Tokens.RELATIVE:
			return instr

		return (mode, mne, value - addr - 2)

	def compute_bytes(output):
		code = []

		def append_little_endian(value):
			code.append(value % 0x100)
			code.append(value // 0x100)

		def append_relative(value):
			if value < 0:
				code.append(0xFF + value + 1)
			else:
				code.append(value)

		for instr in output:
			mode, mne, value = instr
			
			if mode is Tokens.NO_PARAM:
				code.append(opcodes[(mne, Tokens.NO_PARAM)])
			else:
				code.append(opcodes[(mne, mode)])

				if mode is Tokens.RELATIVE:
					append_relative(value)
				elif mode in {Tokens.IMMEDIATE, Tokens.X_INDIRECT, Tokens.INDIRECT_Y, Tokens.RELATIVE, Tokens.ZERO, Tokens.ZERO_X, Tokens.ZERO_Y}:
					code.append(value)
				else:
					append_little_endian(value)

		return code

	sem_output.append((Tokens.NO_PARAM, 'brk', None, None))
	output = [deduce_addressing_mode(x) for x in sem_output]
	size_table = [compute_size(x) for x in output]
	address_table = compute_address(size_table)
	output = [sub_params(addr, instr, address_table) for addr, instr in zip(address_table, output)]
	output = [patch_relative_param(addr, instr) for addr, instr in zip(address_table, output)]
	code = compute_bytes(output)

	return code

if __name__ == '__main__':
	with open('test.asm') as file:
		code = generate_code(analyze_semantics(Parser(make_syntax_analyzer(Peeker(make_tokenizer(file.read()))))))
		print(code)
