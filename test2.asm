;test
init:
  jsr 1illegallabel
  jsr initSnake2
  jsr generateApplePosition
  rts
  jsr $0000
  jsr $00

1IllegalLabel:
	jsr			legalLabel

\\IllegalLabel:
	jsr legalLabel
____legalL__abel: