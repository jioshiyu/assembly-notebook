; ===== 原始作业源码（mycode.asm，由 emu8086 的 .~asm 还原；由 GBK 转 UTF-8；仅存档对照）=====
.MODEL SMALL
.STACK 100h
.DATA
mydata db 12h,34h,56h,78h
len=$-mydata
table db 18h,34h,05h,06h,09h,0ah,0ch,11h,12h,14h

.CODE
START:
mov ax,@data;
mov ds,ax

mov ax,0
mov es,ax
mov si,offset mydata
mov di,0
mov cx,len
rep movsb
mov al,len


push 0435h
push 5c79h
pop ax
pop ax

lea bx,table
mov al,8
xlat


mov al,01111111b
mov bl,00000001b
add al,bl

mov al,11111111b
mov bl,00000001b
add al,bl

mov ah,4ch
int 21h
END START



; [SOURCE]: D:\emu8086\emu8086\MySource\mycode.asm
