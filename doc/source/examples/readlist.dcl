; Read a list, end input with 0
PSH                ; store 0 as end marker
INPUT_LOOP:
INM VALUE          ; read a value from the user
LDA VALUE
JZE DONE_READING   ; if (i == 0) break;
PSH                ; push the value onto the stack
JMP INPUT_LOOP

DONE_READING:      
POPM VALUE         ; pop from the stack
LDA VALUE
JZE ENDE           ; if (i == 0) break;
OUT VALUE          ; output the value
JMP DONE_READING

ENDE:
END

VALUE: DEF 0
