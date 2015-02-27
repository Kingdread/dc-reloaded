; This simple program counts from zero to ten
LOOP:
; load the current value
LDA VALUE
; output the current value
OUT VALUE
; increase by one
INC
; and save back
STA VALUE
; have we reached ten yet?
SUB TEN
; i <= 10 -> i - 10 <= 0
JNP LOOP
END

VALUE: DEF 0
TEN: DEF 10
