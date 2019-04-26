'''
Calculadora de numero en hexadecimal para programar los registros del generador de senales

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

sysclk = 100*10**6
def FTW_calc(frec):
    N = 48
    FTW = int(round((frec*2**N)/sysclk))
    FTW_hex = (hex(FTW)[2:].zfill(13))[0:-1]
    return FTW_hex
def Freq_calc(FTW):
    N = 48
    Freq = round((FTW*sysclk)/(2**N))
    return Freq
def Freq_calc_hex(FTW_hex):
    N = 48
    FTW = int(FTW_hex, 16)
    Freq = round((FTW*sysclk)/(2**N))
    return Freq
def sysclk_calc(FTW_hex, frec):     #borrar esto
    N = 48
    FTW = int(FTW_hex, 16)
    sysclk = int(round((frec*2**N)/FTW))
    return sysclk
def ramp_rate(tiempo):
    Num = tiempo*sysclk - 1
    Num_hex = (hex(int(Num))[2:].zfill(6))
    return Num_hex
def update_rate(tiempo):
    Num = tiempo*sysclk/2 - 1
    Num_hex = (hex(int(Num))[2:].zfill(8))
    if len(Num_hex) == 9:
            Num_hex = (hex(int(Num))[2:].zfill(8))[0:-1]
    return Num_hex

