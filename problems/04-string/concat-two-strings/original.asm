; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    STRING1 DB 'HELLO$'
    STRING2 DB 'WORLD$'
    DEST DB 20 DUP(0)
.CODE
START:   
    MOV AX,@DATA
    MOV DS,AX
    MOV ES,AX
    
    LEA SI,STRING1
    LEA DI,DEST
    MOV CX,5
    CLD
    REP MOVSB
    
    LEA SI,STRING2
    MOV CX,5
    REP MOVSB
    
    MOV AL,'$'
    STOSB
    
    LEA DX,DEST
    MOV AH,9
    INT 21H
    
    MOV AH,4CH
    INT 21H
    
END START
