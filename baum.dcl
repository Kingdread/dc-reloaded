N DEF 0
P DEF 0
TRUE DEF 1
FALSE DEF 0

INM N
PSH ; ruckgabe
PSHM N ; param
JSR primzahl
POP ; param
POP ; ruckgabe
JZE zerlegen
OUT N
END

zerlegen:
LDA N
DEC
STA P
zschleife:
    PSH ; ruckgabe
    PSHM P ; param
    JSR primzahl
    POP ; param
    POP ; ruckgabe
    JZE noprime
    
    ; p ist prim
    treffer:
        PSH ; ruckgabe
        PSHM N ; param
        PSHM P ; param
        JSR teilbar
        POP ; param
        POP ; param
        POP ; ruckgabe
        JZE noprime
        
        ; n ist durch p teilbar
        LDA N
        OUT P
        PSH ; ruck
        PSH ; DIVONE
        LDA P
        PSH ; DIVTWO
        JSR teile
        POP ; DIVTWO
        POP ; DIVONE
        POP ; ruck
        STA N
        JMP treffer

    noprime:
        LDA P
        DEC
        STA P
        DEC
        JPL zschleife
        
END


teile: ; DIVONE / DIVTWO
    LDA FALSE
    PSH
    DIVONE EQUAL 4
    DIVTWO EQUAL 3
    RET EQUAL 5
    I EQUAL 1
    asdf:
        LDAS DIVONE
        SUBS DIVTWO
        STAS DIVONE
        JMS endteile
        LDAS I
        INC
        STAS I
        JMP asdf
    
    endteile:
    LDAS I
    STAS RET
    POP
    RTN
    
; teilbar?
teilbar:
    DIV EQUAL 2
    ZAHL EQUAL 3
    RUCK EQUAL 4
    LDAS ZAHL
    teilloop:
        SUBS DIV
        JPL teilloop
    JMS no
    LDA TRUE
    STAS RUCK
    RTN
    no:
        LDA FALSE
        STAS RUCK
        RTN

; primzahl?
primzahl:
    TEILER EQUAL 2
    ZAHLX EQUAL 4
    RUCKX EQUAL 5
    PSH
    PSHB
    SPBP
    LDAB ZAHLX
    DEC
    JZE primno
    DEC
    JZE primja
    LDAB ZAHLX
    STAB TEILER
    primrepeat:
        LDAB TEILER
        DEC
        STAB TEILER
        DEC
        DEC
        JMS primja
        
        PSH ; ruckgabe
        LDAB ZAHLX
        PSH ; 1. param
        LDAB TEILER
        PSH  ; 2. param
        JSR teilbar
        POP ; 2. param
        POP ; 3. param
        POP ; ruckgabe
        JZE primrepeat
    primno:
        LDA FALSE
        STAB RUCKX
        POPB
        POP
        RTN
    primja:
        LDA TRUE
        STAB RUCKX
        POPB
        POP
        RTN