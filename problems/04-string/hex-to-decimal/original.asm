; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H

.DATA
    NUM DW 8C5Eh            
    BCD DB 5 DUP(0)         
    ASC DB 6 DUP('$')       
    MSG DB 0DH,0AH,'BCD: $'

.CODE
START:
    MOV AX, @DATA
    MOV DS, AX
    MOV ES, AX

    MOV AX, NUM
    LEA DI, BCD
    ADD DI, 4               
    MOV CX, 5
CONVERT:
    MOV DX, 0
    MOV BX, 10
    DIV BX                  
    MOV [DI], DL           
    DEC DI
    LOOP CONVERT

    LEA SI, BCD
    LEA DI, ASC
    MOV CX, 5
    CLD
TRANS:
    LODSB                   
    ADD AL, '0'             
    STOSB                   
    LOOP TRANS

    LEA DX, MSG
    MOV AH, 9
    INT 21H
    LEA DX, ASC
    MOV AH, 9
    INT 21H

    MOV AH, 4CH
    INT 21H
END START
