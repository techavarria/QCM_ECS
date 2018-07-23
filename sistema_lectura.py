#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Comunicacion serial con modulo termoelectrico

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

from threading import Thread
import time
import serial

last_received = ''
fin = 0

def receiving(ser):
    global last_received
    global fin
    buffer = ''
    while not(fin):
        try:
            buffer = buffer + ser.read(ser.inWaiting())
            if '\r\n' in buffer:
                lines = buffer.split('\r\n')
                last_received = lines[-2]
                buffer = lines[-1]
                
        except:
            print ("Excepcion: Abortando...")
            fin = 1
            break
            
class SerialData(object):
    def __init__(self, puerto, init=50, SysInput=bytearray()):
        try:
            # print('puertos son: ')
            # print(ser.serial_ports())
            self.ser = serial.Serial(
                # port='/dev/ttyACM0', # Para sistemas Unix-Like
                # port=ser.serial_ports()[1],#'COM16',  #Para sistemas no UNIX   #SE CAMBIO DE 0 A 1 PARA QUE COJA EL SEGUNDO PUERTO QUE ENLISTA
                port=puerto,        #'COM16'
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.01,
                xonxoff=0,
                rtscts=0,
                interCharTimeout=None
            )
            self.fin = 0
        except serial.serialutil.SerialException:
            self.ser = None
            print('No hay conexion serial')
        else:
            self.t = Thread(target=receiving, args=(self.ser,))
            self.t.start()
            
    def next(self, emitting):
        self.ser.write(emitting)
        time.sleep(0.02)
        if not self.ser:
            print("sin conexion")
            return [0.0, 0.0, 0.0, 0.0]

        for i in range(5):
            try:
                raw_line = last_received
                return (raw_line)
            except ValueError:
                print('Sin Datos', raw_line)
                time.sleep(.005)
                return [0.0]
        
    def __del__(self):
        if self.ser:
            print("close")  
            self.ser.close()
            self.t.join()

if __name__=='__main__':
    s = SerialData('/dev/ttyACM0')
    print(s.next('$V\r'))   #Informacion ID
