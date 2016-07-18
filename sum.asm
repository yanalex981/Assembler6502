define sum 0
define i 10

	lda sum
	ldx i
loop:
	cpx #10
	beq end
	inx
	stx i
	adc i
	jmp loop
end:
	brk