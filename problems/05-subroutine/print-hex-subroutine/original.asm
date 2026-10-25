; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    NUM DW 1000110001011110B
.CODE
PRINT_HEX PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    
    MOV BX,AX
    MOV CX,4
    
NEXT_DIGIT:
    ROL BX,4
    MOV DL,BL
    AND DL,0FH
    
    CMP DL,10
    JL IS_DIGIT
    ADD DL,7
    
IS_DIGIT:
    ADD DL,'0' 
    MOV AH,2
    INT 21H
    LOOP NEXT_DIGIT
    
    MOV DL,'H'
    MOV AH,2 
    INT 21H
    
    POP DX
    POP CX
    POP BX
    POP AX
    RET

PRINT_HEX ENDP
START:
    MOV AX,@DATA
    MOV DS,AX
    
    MOV AX,NUM
    CALL PRINT_HEX
    
    MOV AH,4CH
    INT 21H
END START
