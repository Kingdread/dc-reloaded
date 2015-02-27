; Calculate the nth fibonacci number
; Warning: Very slow! Uses recursion and thus has exponential growth.
; Only for demonstration purposes
; fib(n) = fib(n-1) + fib(n-2)
; fib(0) = 0
; fib(1) = 1
; 0 1 1 2 3 5
; Input 5, Output: 5

INM VALUE
PSHM VALUE   ; argument
PSH          ; return value
JSR FIBONACCI
POPM VALUE   ; return value
POP          ; argument
OUT VALUE
END

; int fibonacci(int n) {
FIBONACCI:
PSH          ; one local variable for the sum
PSHB         ; save the base pointer
SPBP         ; from now on we can use BP for locals
ARG EQUAL 5  ; the argument is at BP+5
RET EQUAL 4  ; the return value is at BP+4
             ; the return address is at BP+3
SUM EQUAL 2  ; the local variable is at BP+2
             ; the saved base pointer is at BP+1
LDAB ARG     ; load the given argument
JZE FIB_ZERO ; fib(0) shortcut
DEC          ; n = n - 1
JZE FIB_ONE  ; fib(1) shortcut

PSH          ; argument for first recursion call
PSH          ; space for return value of first recursion
JSR FIBONACCI
POP          ; load the return value
STAB SUM     ; save to local variable
POP          ; remove argument from stack
DEC          ; n = n - 2
PSH          ; argument for second recursion call
PSH          ; space for return value of second recursion
JSR FIBONACCI
POP          ; load the return value
ADDB SUM     ; add the previous result
STAB RET     ; and save the result to the return position
POP          ; remove argument from stack 
JMP FIB_RETURN

FIB_ZERO:
LDA CONST_ZERO
STAB RET
JMP FIB_RETURN

FIB_ONE:
LDA CONST_ONE
STAB RET
JMP FIB_RETURN

FIB_RETURN:
POPB         ; restore the base pointer
POP          ; remove the local variable
RTN          ; jump back to the caller
; }

VALUE: DEF 0
CONST_ZERO: DEF 0
CONST_ONE: DEF 1
