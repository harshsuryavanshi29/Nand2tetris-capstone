// Box.asm - Keyboard controlled black box
// K = 71
// Starting address = 18656
// Height = 20 rows
// Width = 64 pixels (4 words)

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE

    @color
    M=0
    @DRAW
    0;JMP

(BLACK)
    @color
    M=-1

(DRAW)
    @18656
    D=A
    @addr
    M=D

    @20
    D=A
    @rows
    M=D

(ROWLOOP)
    @rows
    D=M
    @LOOP
    D;JEQ

    @addr
    D=M
    @p
    M=D

    @4
    D=A
    @cnt
    M=D

(COLLOOP)
    @color
    D=M
    @p
    A=M
    M=D

    @p
    M=M+1

    @cnt
    MD=M-1
    @COLLOOP
    D;JGT

    @addr
    D=M
    @32
    D=D+A
    @addr
    M=D

    @rows
    M=M-1
    @ROWLOOP
    0;JMP