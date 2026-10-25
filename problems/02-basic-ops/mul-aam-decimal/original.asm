; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100
.DATA
.CODE
START:
    MOV BL,08H
    MOV CL,07H
    MOV AL,BL
    MUL CL
    AAM
    MOV DH,AH
    MOV DL,AL 
    
    MOV AH,4CH
    INT 21H
END START
