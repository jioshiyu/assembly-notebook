; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    STR DB 'THIS IS A TEST!',0
.CODE
PRINT_STACK PROC
    PUSH BP
    MOV BP,SP
    PUSH AX
    PUSH SI
    MOV SI,[BP+4] 
    MOV AH,2
NEXT:
    MOV AL,[SI]
    CMP AL,'!'                                                                  
    JE DONE
    MOV DL,AL
    INT 21H
    INC SI
    JMP NEXT
    
DONE:
    POP SI
    POP AX
    POP BP
    RET 2
    
PRINT_STACK ENDP
START:
    MOV AX,@DATA
    MOV DS,AX
    
    LEA AX,STR  
    PUSH AX
    CALL PRINT_STACK
    
    MOV AH,4CH
    INT 21H

END START
