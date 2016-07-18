from enum import Enum
from syntax_analyzer import Tokens as syn
from syntax_analyzer import make_syntax_analyzer
from peeker import Peeker
from tokenizer import make_tokenizer
from semantic_analyzer import analyze_semantics

def generate_code(tree, output_file, start_address=0):
	opcodes = {
		('brk', Addr.NO_PARAM) : 0x00, ('ora', Addr.X_INDIRECT): 0x01,                                                             ('ora', Addr.ZERO)  : 0x05, ('asl', Addr.ZERO)  : 0x06, ('php', Addr.NO_PARAM): 0x08, ('ora', Addr.IMMEDIATE) : 0x09, ('asl', Addr.NO_PARAM): 0x0A,                                 ('ora', Addr.ABSOLUTE)  : 0x0D, ('asl', Addr.ABSOLUTE)  : 0x0E,
		('bpl', Addr.RELATIVE) : 0x10, ('ora', Addr.INDIRECT_Y): 0x11,                                                             ('ora', Addr.ZERO_X): 0x15, ('asl', Addr.ZERO_X): 0x16, ('clc', Addr.NO_PARAM): 0x18, ('ora', Addr.ABSOLUTE_Y): 0x19,                                                               ('ora', Addr.ABSOLUTE_X): 0x1D, ('asl', Addr.ABSOLUTE_X): 0x1E,
		('jsr', Addr.ABSOLUTE) : 0x20, ('and', Addr.X_INDIRECT): 0x21,                                 ('bit', Addr.ZERO)  : 0x24, ('and', Addr.ZERO)  : 0x25, ('rol', Addr.ZERO)  : 0x26, ('plp', Addr.NO_PARAM): 0x28, ('and', Addr.IMMEDIATE) : 0x29, ('rol', Addr.NO_PARAM): 0x2A, ('bit', Addr.ABSOLUTE)  : 0x2C, ('and', Addr.ABSOLUTE)  : 0x2D, ('rol', Addr.ABSOLUTE)  : 0x2E,
		('bmi', Addr.RELATIVE) : 0x30, ('and', Addr.INDIRECT_Y): 0x31,                                                             ('and', Addr.ZERO_X): 0x35, ('rol', Addr.ZERO_X): 0x36, ('sec', Addr.NO_PARAM): 0x38, ('and', Addr.ABSOLUTE_Y): 0x39,                                                               ('and', Addr.ABSOLUTE_X): 0x3D, ('rol', Addr.ABSOLUTE_X): 0x3E,
		('rti', Addr.NO_PARAM) : 0x40, ('eor', Addr.X_INDIRECT): 0x41,                                                             ('eor', Addr.ZERO)  : 0x45, ('lsr', Addr.ZERO)  : 0x46, ('pha', Addr.NO_PARAM): 0x48, ('eor', Addr.IMMEDIATE) : 0x49, ('lsr', Addr.NO_PARAM): 0x4A, ('jmp', Addr.ABSOLUTE)  : 0x4C, ('eor', Addr.ABSOLUTE)  : 0x4D, ('lsr', Addr.ABSOLUTE)  : 0x4E,
		('bvc', Addr.RELATIVE) : 0x50, ('eor', Addr.INDIRECT_Y): 0x51,                                                             ('eor', Addr.ZERO_X): 0x55, ('lsr', Addr.ZERO_X): 0x56, ('cli', Addr.NO_PARAM): 0x58, ('eor', Addr.ABSOLUTE_Y): 0x59,                                                               ('eor', Addr.ABSOLUTE_X): 0x5D, ('lsr', Addr.ABSOLUTE_X): 0x5E,
		('rts', Addr.NO_PARAM) : 0x60, ('adc', Addr.X_INDIRECT): 0x61,                                                             ('adc', Addr.ZERO)  : 0x65, ('ror', Addr.ZERO)  : 0x66, ('pla', Addr.NO_PARAM): 0x68, ('adc', Addr.IMMEDIATE) : 0x69, ('ror', Addr.NO_PARAM): 0x6A, ('jmp', Addr.INDIRECT)  : 0x6C, ('adc', Addr.ABSOLUTE)  : 0x6D, ('ror', Addr.ABSOLUTE)  : 0x6E,
		('bvs', Addr.RELATIVE) : 0x70, ('adc', Addr.INDIRECT_Y): 0x71,                                                             ('adc', Addr.ZERO_X): 0x75, ('ror', Addr.ZERO_X): 0x76, ('sei', Addr.NO_PARAM): 0x78, ('adc', Addr.ABSOLUTE_Y): 0x79,                                                               ('adc', Addr.ABSOLUTE_X): 0x7D, ('ror', Addr.ABSOLUTE_X): 0x7E,
		                               ('sta', Addr.X_INDIRECT): 0x81,                                 ('sty', Addr.ZERO)  : 0x84, ('sta', Addr.ZERO)  : 0x85, ('stx', Addr.ZERO)  : 0x86, ('dey', Addr.NO_PARAM): 0x88,                                 ('txa', Addr.NO_PARAM): 0x8A, ('sty', Addr.ABSOLUTE)  : 0x8C, ('sta', Addr.ABSOLUTE)  : 0x8D, ('stx', Addr.ABSOLUTE)  : 0x8E,
		('bcc', Addr.RELATIVE) : 0x90, ('sta', Addr.INDIRECT_Y): 0x91,                                 ('sty', Addr.ZERO_X): 0x94, ('sta', Addr.ZERO_X): 0x95, ('stx', Addr.ZERO_Y): 0x96, ('tya', Addr.NO_PARAM): 0x98, ('sta', Addr.ABSOLUTE_Y): 0x99, ('txs', Addr.NO_PARAM): 0x9A,                                 ('sta', Addr.ABSOLUTE_X): 0x9D,
		('ldy', Addr.IMMEDIATE): 0xA0, ('lda', Addr.X_INDIRECT): 0xA1, ('ldx', Addr.IMMEDIATE) : 0xA2, ('ldy', Addr.ZERO)  : 0xA4, ('lda', Addr.ZERO)  : 0xA5, ('ldx', Addr.ZERO)  : 0xA6, ('tay', Addr.NO_PARAM): 0xA8, ('lda', Addr.IMMEDIATE) : 0xA9, ('tax', Addr.NO_PARAM): 0xAA, ('ldy', Addr.ABSOLUTE)  : 0xAC, ('lda', Addr.ABSOLUTE)  : 0xAD, ('ldx', Addr.ABSOLUTE)  : 0xAE,
		('bcs', Addr.RELATIVE) : 0xB0, ('lda', Addr.INDIRECT_Y): 0xB1,                                 ('ldy', Addr.ZERO_X): 0xB4, ('lda', Addr.ZERO_X): 0xB5, ('ldx', Addr.ZERO_Y): 0xB6, ('clv', Addr.NO_PARAM): 0xB8, ('lda', Addr.ABSOLUTE_Y): 0xB9, ('tsx', Addr.NO_PARAM): 0xBA, ('ldy', Addr.ABSOLUTE_X): 0xBC, ('lda', Addr.ABSOLUTE_X): 0xBD, ('ldx', Addr.ABSOLUTE_X): 0xBE,
		('cpy', Addr.IMMEDIATE): 0xC0, ('cmp', Addr.X_INDIRECT): 0xC1,                                 ('cpy', Addr.ZERO)  : 0xC4, ('cmp', Addr.ZERO)  : 0xC5, ('dec', Addr.ZERO)  : 0xC6, ('iny', Addr.NO_PARAM): 0xC8, ('cmp', Addr.IMMEDIATE) : 0xC9, ('dex', Addr.NO_PARAM): 0xCA, ('cpy', Addr.ABSOLUTE)  : 0xCC, ('cmp', Addr.ABSOLUTE)  : 0xCD, ('dec', Addr.ABSOLUTE)  : 0xCE,
		('bne', Addr.RELATIVE) : 0xD0, ('cmp', Addr.INDIRECT_Y): 0xD1,                                                             ('cmp', Addr.ZERO_X): 0xD5, ('dec', Addr.ZERO_X): 0xD6, ('cld', Addr.NO_PARAM): 0xD8, ('cmp', Addr.ABSOLUTE_Y): 0xD9,                                                               ('cmp', Addr.ABSOLUTE_X): 0xDD, ('dec', Addr.ABSOLUTE_X): 0xDE,
		('cpx', Addr.IMMEDIATE): 0xE0, ('sbc', Addr.X_INDIRECT): 0xE1,                                 ('cpx', Addr.ZERO)  : 0xE4, ('sbc', Addr.ZERO)  : 0xE5, ('inc', Addr.ZERO)  : 0xE6, ('inx', Addr.NO_PARAM): 0xE8, ('sbc', Addr.IMMEDIATE) : 0xE9, ('nop', Addr.NO_PARAM): 0xEA, ('cpx', Addr.ABSOLUTE)  : 0xEC, ('sbc', Addr.ABSOLUTE)  : 0xED, ('inc', Addr.ABSOLUTE)  : 0xEE,
		('beq', Addr.RELATIVE) : 0xF0, ('sbc', Addr.INDIRECT_Y): 0xF1,                                                             ('sbc', Addr.ZERO_X): 0xF5, ('inc', Addr.ZERO_X): 0xF6, ('sed', Addr.NO_PARAM): 0xF8, ('sbc', Addr.ABSOLUTE_Y): 0xF9,                                                               ('sbc', Addr.ABSOLUTE_X): 0xFD, ('inc', Addr.ABSOLUTE_X): 0xFE
	}

	def deduce_addressing_mode(instr):
		def deduce(mode, mne, data_type, value):
			if mode is syn.ONE_PARAM:
				if (mne, Addr.RELATIVE) in opcodes:
					return (Addr.RELATIVE, mne, data_type, value)
				elif (mne, Addr.ZERO) in opcodes and value < 256:
					return (Addr.ZERO, mne, data_type, value)
				elif (mne, Addr.ABSOLUTE) in opcodes:
					return (Addr.ABSOLUTE, mne, data_type, value)
			elif mode is syn.X_INDEX:
				if (mne, Addr.ZERO_X) in opcodes and value < 256:
					return (Addr.ZERO_X, mne, data_type, value)
				elif (mne, Addr.ABSOLUTE_X) in opcodes:
					return (Addr.ABSOLUTE_X, mne, data_type, value)
			elif mode is syn.Y_INDEX:
				if (mne, Addr.ZERO_Y) in opcodes and value < 256:
					return (Addr.ZERO_Y, mne, data_type, value)
				elif (mne, Addr.ABSOLUTE_Y) in opcodes:
					return (Addr.ABSOLUTE_Y, mne, data_type, value)

			raise Exception('Cannot deduce addressing mode for "{} {} {}:{}"'.format(mne, mode, data_type, value))

		mode, mne, *_ = instr

		if mode in {syn.ONE_PARAM, syn.X_INDEX, syn.Y_INDEX}:
			return deduce(*instr)
		else:
			return instr

	def compute_size(instr):
		mode, mne, *_ = instr

		if mode is syn.NO_PARAM:
			# return (1, mode, mne)
			return 1

		mode, mne, data_type, value = instr

		if mode in [syn.IMMEDIATE, syn.X_INDIRECT, syn.INDIRECT_Y, Addr.RELATIVE, Addr.ZERO, Addr.ZERO_X, Addr.ZERO_Y]:
			# return (2, mode, mne, data_type, value)
			return 2
		else:
			# return (3, mode, mne, data_type, value)
			return 3

	def compute_address(start_address, size_table):
		address = start_address
		address_table = []

		for size in size_table:
			address_table.append(address)
			address += size

		return address_table

	def sub_params(addr, instr, address_table):
		mode, mne, *_ = instr
		
		if mode is syn.NO_PARAM:
			return instr

		mode, mne, data_type, value = instr

		if data_type is syn.LABEL:
			return (mode, mne, address_table[value])
		
		if data_type is syn.CONSTANT:
			return (mode, mne, value)

	def patch_relative_param(addr, instr):
		mode, mne, *_ = instr

		if mode is not Addr.RELATIVE:
			return instr

		mode, mne, value = instr

		return (mode, mne, value - addr - 2)

	def compute_bytes(instr):
		mode, mne, *_ = instr

		if mode is syn.NO_PARAM:
			return [opcodes[(mne, Addr.NO_PARAM)]]

		if mode in {syn.}:
			pass

	tree.append((syn.NO_PARAM, 'brk'))
	processed_tree = [deduce_addressing_mode(x) for x in tree]
	size_table = [compute_size(x) for x in processed_tree]
	address_table = compute_address(start_address, size_table)
	processed_tree = [sub_params(addr, instr, address_table) for addr, instr in zip(address_table, processed_tree)]
	processed_tree = [patch_relative_param(addr, instr) for addr, instr in zip(address_table, processed_tree)]
	code = [compute_bytes(instr) for instr in processed_tree]

	print(code)
	print()

	return processed_tree

if __name__ == '__main__':
	with open('test.asm') as file:
		print(generate_code(analyze_semantics(make_syntax_analyzer(Peeker(make_tokenizer(file.read())))), None))
