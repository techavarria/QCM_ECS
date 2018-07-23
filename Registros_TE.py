# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 13:02:27 2017

@author: lab_kiron
"""

dicc={'Register': 
                    {'stp': 0,
                     'Kp': 1,
                     'Ki': 2,
                     'Kd': 3,
                     'KLP_A': 4,
                     'KLP_B': 5,
                     'TcLimit': 6,
                     'TcDeadBand': 7,
                     'iLim': 8,
                     'Ts': 9,
                     'Cool Gain': 10,
                     'Heat Gain': 11,
                     'Decay': 12,
                     'REGULATOR MODE': 13,
                     'Dead band value': 14,
                     'Hysteresis value': 15,
                     'F1MS': 16,
                     'F1 ST': 17,
                     'F1 Dead band': 18,
                     'F1LSH': 19,
                     'F1HSH': 20,
                     'F1LSV': 21,
                     'F1HSV': 22,
                     'F2MS': 23,
                     'F2 ST': 24,
                     'FAN2 Dead band': 25,
                     'F2LSH': 26,
                     'F2HSH': 27,
                     'F2LSV': 28,
                     'F2HSV': 29,
                     'POTiAD': 30,
                     'POTioffset': 31,
                     'POTigain': 32,
                     'EpADout_offset': 33,
                     'EpADout_gain': 34,
                     'T1_gain': 35,
                     'T1_offset': 36,
                     'T2_gain': 37,
                     'T2_offset': 38,
                     'T3_gain': 39,
                     'T3_offset': 40,
                     'Tfet_gain': 41,
                     'Tfet_offset': 42,
                     'T1dpo': 43,
                     'T1dpg': 44,
                     'ALVH': 45,
                     'ALVL': 46,
                     'ALMCH': 47,
                     'ALMCL': 48,
                     'ALF1CH': 49,
                     'ALF1CL': 50,
                     'ALF2CH': 51,
                     'ALF2CL': 52,
                     'ALI12H': 53,
                     'ALI12L': 54,
                     'T1MODE': 55,
                     'T2MODE': 56,
                     'T3MODE': 57,
                     'T4MODE': 58,
                     'T1SCA': 59,
                     'T1SCB': 60,
                     'T1SCC': 61,
                     'T2SCA': 62,
                     'T2SCB': 63,
                     'T2SCC': 64,
                     'T3SCA': 65,
                     'T3SCB': 66,
                     'T3SCC': 67,
                     'T4SCA': 68,
                     'T4SCB': 69,
                     'T4SCC': 70,
                     'AT1H': 71,
                     'AT1L': 72,
                     'AT2H': 73,
                     'AT2L': 74,
                     'AT3H': 75,
                     'AT3L': 76,
                     'AT4H': 77,
                     'AT4L': 78,
                     'T1SRH': 79,
                     'T1SRM': 80,
                     'T1SRL': 81,
                     'T2SRH': 82,
                     'T2SRM': 83,
                     'T2SRL': 84,
                     'T3SRH': 85,
                     'T3SRM': 86,
                     'T3SRL': 87,
                     'T4SRH': 88,
                     'T4SRM': 89,
                     'T4SRL': 90,
                     'AEBL': 91,
                     'AEBH': 92,
                     'stp2': 93,
                     'TH': 94,
                     'TL': 95,
                     'SAM': 96,
                     'REC': 99,
                     'T1V': 100,
                     'T2V': 101,
                     'T3V': 102,
                     'TFETV': 103,
                     'TPOT': 104,
                     'TREF': 105,
                     'TC': 106,
                     'F1OUTPUT': 107,
                     'F2OUTPUT': 108,
                     'Ta': 110,
                     'Te': 111,
                     'Tp': 112,
                     'Ti': 113,
                     'Td': 114,
                     'TLP_A': 117,
                     'TLP_B': 118,
                     'rts': 122,
                     'rtmax': 123,
                     'rtmin': 124,
                     'F1rts': 125,
                     'F1rtmax': 126,
                     'F1rtmin': 127,
                     'F2rts': 128,
                     'F2rtmax': 129,
                     'F2rtmin': 130,
                     'AN1': 150,
                     'AN10': 151,
                     'AN9': 152,
                     'AN11': 153,
                     'AN4': 154,
                     'No usar': 155},
    'Description': {'stp': 'Set Point - (fgTref) Main temperature reference',
                     'Kp': 'PID – (Kp) P constant',
                     'Ki': 'PID – (Ki) I constant',
                     'Kd': 'PID – (Kd) D constant',
                     'KLP_A': 'PID – (KLP_A) Low pass filter A (+value)',
                     'KLP_B': 'PID – (KLP_B) Low pass filter B (+value)',
                     'TcLimit': 'MAIN – (TcLimit) Limit the Tc signal (0..100)',
                     'TcDeadBand': 'MAIN – (TcDeadBand) Dead band of Tc signal',
                     'iLim': 'PID – (iLim) Limit I value (0..100)',
                     'Ts': 'MAIN – (Ts) Sample rate 1/Hz',
                     'Cool Gain': 'MAIN – (Cool Gain) Gain of cool part of Tc signal',
                     'Heat Gain': 'MAIN – (Heat Gain) Gain of heat part of Tc signal',
                     'Decay': 'PID – (Decay) Decay of I and low pass filter part',
                     'REGULATOR MODE': 'REGULATOR MODE – Control register',
                     'Dead band value': 'ON/OFF Dead band (+value)',
                     'Hysteresis value': 'ON/OFF Hysteresis (+value)',
                     'F1MS': 'FAN 1 Mode select',
                     'F1 ST': 'FAN 1 Set temperature',
                     'F1 Dead band': 'FAN 1 Dead band (+value)',
                     'F1LSH': 'FAN 1 Low speed hysteresis (+value)',
                     'F1HSH': 'FAN 1 High speed hysteresis (+value)',
                     'F1LSV': 'FAN 1 Low Speed voltage (0..30)',
                     'F1HSV': 'FAN 1 High Speed voltage (0..30)',
                     'F2MS': 'FAN 2 Mode select',
                     'F2 ST': 'FAN 2 Set temperature',
                     'FAN2 Dead band': 'FAN 2 Dead band (+value)',
                     'F2LSH': 'FAN 2 Low speed hysteresis (+value)',
                     'F2HSH': 'FAN 2 High speed hysteresis (+value)',
                     'F2LSV': 'FAN 2 Low Speed voltage (0..30)',
                     'F2HSV': 'FAN 2 High Speed voltage (0..30)',
                     'POTiAD': 'POT input - AD offset',
                     'POTioffset': 'POT input - offset',
                     'POTigain': 'POT input - gain',
                     'EpADout_offset': 'Expansion port AD out – offset',
                     'EpADout_gain': 'Expansion port AD out - gain',
                     'T1_gain': 'Temp 1 gain',
                     'T1_offset': 'Temp 1 offset',
                     'T2_gain': 'Temp 2 gain',
                     'T2_offset': 'Temp 2 offset',
                     'T3_gain': 'Temp 3 gain',
                     'T3_offset': 'Temp 3 offset',
                     'Tfet_gain': 'Temp FET gain',
                     'Tfet_offset': 'Temp FET offset',
                     'T1dpo': 'Temp 1 digital pot offset (0..255)',
                     'T1dpg': 'Temp 1 digital pot gain (0..255)',
                     'ALVH': 'ALARM level voltage high',
                     'ALVL': 'ALARM level voltage low',
                     'ALMCH': 'ALARM level main current high',
                     'ALMCL': 'ALARM level main current low',
                     'ALF1CH': 'ALARM level FAN 1 current high',
                     'ALF1CL': 'ALARM level FAN 1 current low',
                     'ALF2CH': 'ALARM level FAN 2 current high',
                     'ALF2CL': 'ALARM level FAN 2 current low',
                     'ALI12H': 'ALARM level internal 12v high',
                     'ALI12L': 'ALARM level internal 12v low',
                     'T1MODE': 'Temp1 mode',
                     'T2MODE': 'Temp2 mode',
                     'T3MODE': 'Temp3 mode',
                     'T4MODE': 'Temp4 mode',
                     'T1SCA': 'Temp1 Steinhart coeff A',
                     'T1SCB': 'Temp1 Steinhart coeff B',
                     'T1SCC': 'Temp1 Steinhart coeff C',
                     'T2SCA': 'Temp2 Steinhart coeff A',
                     'T2SCB': 'Temp2 Steinhart coeff B',
                     'T2SCC': 'Temp2 Steinhart coeff C',
                     'T3SCA': 'Temp3 Steinhart coeff A',
                     'T3SCB': 'Temp3 Steinhart coeff B',
                     'T3SCC': 'Temp3 Steinhart coeff C',
                     'T4SCA': 'Temp4 Steinhart coeff A',
                     'T4SCB': 'Temp4 Steinhart coeff B',
                     'T4SCC': 'Temp4 Steinhart coeff C',
                     'AT1H': 'ALARM Temp 1 high',
                     'AT1L': 'ALARM Temp 1 low',
                     'AT2H': 'ALARM Temp 2 high',
                     'AT2L': 'ALARM Temp 2 low',
                     'AT3H': 'ALARM Temp 3 high',
                     'AT3L': 'ALARM Temp 3 low',
                     'AT4H': 'ALARM Temp 4 high',
                     'AT4L': 'ALARM Temp 4 low',
                     'T1SRH': 'Temp1 Steinhart resistance value H',
                     'T1SRM': 'Temp1 Steinhart resistance value M',
                     'T1SRL': 'Temp1 Steinhart resistance value L',
                     'T2SRH': 'Temp2 Steinhart resistance value H',
                     'T2SRM': 'Temp2 Steinhart resistance value M',
                     'T2SRL': 'Temp2 Steinhart resistance value L',
                     'T3SRH': 'Temp3 Steinhart resistance value H',
                     'T3SRM': 'Temp3 Steinhart resistance value M',
                     'T3SRL': 'Temp3 Steinhart resistance value L',
                     'T4SRH': 'Temp4 Steinhart resistance value H',
                     'T4SRM': 'Temp4 Steinhart resistance value M',
                     'T4SRL': 'Temp4 Steinhart resistance value L',
                     'AEBL': 'Alarm enable bits low',
                     'AEBH': 'Alarm enable bits high',
                     'stp2': 'Setpoint 2',
                     'TH': 'TimeHigh',
                     'TL': 'TimeLow',
                     'SAM': 'Sensor Alarm Mask',
                     'REC': 'Regulator event count. Increments one time each regulator event.',
                     'T1V': 'Temp 1 value (AN5)',
                     'T2V': 'Temp 2 value (AN6)',
                     'T3V': 'Temp 3 value (AN7)',
                     'TFETV': 'Temp FET value (AN8)',
                     'TPOT': 'Temp POT reference (AN0)',
                     'TREF': 'TRef',
                     'TC': 'MAIN (Tc) output value (-100..+100)',
                     'F1OUTPUT': 'FAN 1 output value (0..100)',
                     'F2OUTPUT': 'FAN 2 output value (0..100)',
                     'Ta': 'PID – Ta',
                     'Te': 'PID – Te',
                     'Tp': 'PID – Tp',
                     'Ti': 'PID – Ti',
                     'Td': 'PID – Td',
                     'TLP_A': 'PID – TLP_A',
                     'TLP_B': 'PID – TLP_B',
                     'rts': 'ON/OFF – runtime state',
                     'rtmax': 'ON/OFF – runtime max',
                     'rtmin': 'ON/OFF – runtime min',
                     'F1rts': 'FAN1 – runtime state',
                     'F1rtmax': 'FAN1 – runtime max',
                     'F1rtmin': 'FAN1 – runtime min',
                     'F2rts': 'FAN2 – runtime state',
                     'F2rtmax': 'FAN2 - runtime max',
                     'F2rtmin': 'FAN2 – runtime min',
                     'AN1': '(AN1) Input voltage',
                     'AN10': '(AN10) Internal 12v',
                     'AN9': '(AN9) Main current',
                     'AN11': '(AN11) FAN1 current',
                     'AN4': '(AN4) FAN2 current',
                     'No usar': 'FAN1 and FAN2 internal gain value (do not use)'}
    }

def com(tipo, nombre='', valor=None):
    nombre=str(nombre)
    tipo=str(tipo)
    try:
        
        if valor == None :
            if tipo=='Leer':
                if (str(dicc['Register'].get(str(nombre))) == 'None' or nombre == ''  ):
                    raise Sinparametro('')
                else:
                    comando='$' + 'R' + str(dicc['Register'].get(str(nombre))) +'?' '\r'
            else:
                comando='$' + str(tipo) + '\r'
                
        if tipo == 'Escribir':
            if (str(dicc['Register'].get(str(nombre))) == 'None' or valor == None or nombre == ''  ):
                raise Sinparametro('')
            else:
                comando='$' + 'R' + str(dicc['Register'].get(str(nombre))) + '=' + str(valor) + '\r'
            
        
        
        return comando
    
    except Sinparametro as a:
        print('Falta un parámetro o el nombre esta mal escrito', a.value)
        return ''
       
    except:
        
        print('comando no reconocido')
        comando='???'
        return comando
    
def info(nombre):
    informacion=str(dicc['Description'].get(str(nombre)))
    if informacion == 'None':
        print('No existe ese comando')
        return ''
    else:
        return informacion
    
class Sinparametro(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)