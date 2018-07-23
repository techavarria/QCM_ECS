import time
import ser as seri
import serial
import FTW_Freq_calc

def fun_setFreq(frec):
    ser = serial.Serial(seri.serial_ports()[0], 9600, timeout=0.01, parity=serial.PARITY_EVEN, rtscts=0)
    ser.write('02'.decode("hex"))
    FTW_hex = FTW_Freq_calc.FTW_calc(frec)
    ser.write(FTW_hex.decode("hex"))

def fun_setSweep(fi, fp, ff):
    ser = serial.Serial(seri.serial_ports()[0], 9600, timeout=0.01, parity=serial.PARITY_EVEN, rtscts=0)
    for freq in range(fi, ff + fp, fp):
        ser.write('02'.decode("hex"))
        FTW_hex = FTW_Freq_calc.FTW_calc(freq)
        ser.write(FTW_hex.decode("hex"))
