; Read two (positive) integer values from the user and multiply them
; read the values
INM A        ; a = input();
INM B        ; b = input();
; multiplication is just repeated addition
LOOP:
LDA A        ; while (a > 0)
JZE ENDE     ; {
DEC          ;    a--;
STA A        ;
LDA PRODUCT  ;    product = product + b;
ADD B        ;
STA PRODUCT  ;
JMP LOOP     ; }
ENDE:
OUT PRODUCT  ; print(b);
END

A: DEF 0     ; int a;
B: DEF 0     ; int b;
PRODUCT: DEF 0 ; int product;
