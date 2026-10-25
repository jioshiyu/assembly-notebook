; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H

.DATA
    X DB 3
    N DB 5
    MSG DB 'RESULT:$'
    CRLF DB 0DH,0AH,'$'

.CODE
POWER PROC
    CMP CL, 0
    JNE RECURSE
    MOV AX, 1
    RET
RECURSE:
    PUSH AX          
    DEC CL
    CALL POWER
    POP BX           
    MUL BL           
    RET
POWER ENDP

PRINT_AX_DEC PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV BX, 10
    MOV CX, 0
DIV_LOOP:
    MOV DX, 0
    DIV BX
    PUSH DX
    INC CX
    CMP AX, 0
    JNE DIV_LOOP
PRINT_LOOP:
    POP DX
    ADD DL, '0'
    MOV AH, 2
    INT 21H
    LOOP PRINT_LOOP
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_AX_DEC ENDP

START:
    MOV AX, @DATA
    MOV DS, AX

    MOV AL, X
    MOV CL, N
    CALL POWER          

    PUSH AX  
    LEA DX, MSG
    MOV AH, 9
    INT 21H 
    POP AX
    

    CALL PRINT_AX_DEC  

    LEA DX, CRLF
    MOV AH, 9
    INT 21H

    MOV AH, 4CH
    INT 21H
END START
