; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    BUFA DB 'A','B','C','D','E'
    BUFB DB 'C','D','E','F','G'
    BUFC DB 5 DUP(0)
    COUNT DW 0
    MSG DB 'COMMON ELEMENTS: $'
    CRLF DB 0DH,0AH,'$'
    
.CODE
START:
    MOV AX,@DATA 
    MOV DS,AX
    
    LEA SI,BUFA
    MOV CX,5
    
OUTER:
    MOV AL,[SI]
    PUSH CX
    LEA DI,BUFB
    MOV CX,5

INNER:
    CMP AL,[DI]
    JE FOUND
    INC DI
    LOOP INNER
    JMP NOTFOUND

FOUND:
    MOV BX,COUNT
    LEA DI,BUFC
    ADD DI,BX
    MOV [DI],AL
    INC COUNT
NOTFOUND:
    POP CX
    INC SI
    LOOP OUTER
    
    LEA DX,MSG
    MOV AH,9
    INT 21H 
    MOV CX,COUNT
    JCXZ EXIT
    LEA SI,BUFC 
    
DISP:
    MOV DL,[SI]
    MOV AH,2
    INT 21H
    
    MOV DL,' '
    MOV AH,2
    INT 21H
    INC SI
    LOOP DISP
        
EXIT:
    LEA DX,CRLF
    MOV AH,9
    INT 21H 
    MOV AH,4CH
    INT 21H

END START
