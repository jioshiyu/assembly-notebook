; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    A DW 0FFFBH
    A_2 DW 0FFFFH
.CODE
START:
    MOV AX,@DATA
    MOV DS,AX
    MOV AX,A
    MOV DX,A_2
    
    MOV BX,DX
    ADD BX,BX
    SBB BX,BX 
    XOR AX,BX
    XOR DX,BX
    SUB AX,BX
    SBB DX,BX 
    MOV A,AX
    MOV A_2,DX
    
    MOV AH,4CH
    INT 21H
END START
