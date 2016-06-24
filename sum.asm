define sum $100
define i $101

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
	brk