'''
Lee constantemente los valores de amplitud y fase del servidor (CMQTT)
enviados por la raspberry y los va guardando en un archivo csv.

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

import paho.mqtt.client as mqttClient
import time
import csv
from array import array
import numpy as np

class General(object):
    def __init__(self):
        self.frec = 0
        self.tiempo_incial = 0
        self.parar = 0
        self.v_tiempo = []
        self.v_amp = []
        self.v_fase = []
        self.v_bat = []
        self.v_pin1 = []
        self.v_pin2 = []
        self.v_pin3 = []
        self.v_pin4 = []
        self.v_pin5 = []


        self.Connected = False  # global variable for the state of the connection
        broker_address = "m12.cloudmqtt.com"
        port = 17785
        user = "qsbfmyfp"
        password = "zWnhGsM6YoH7"
        self.client = mqttClient.Client("CMQTT_comu")  # create new instance
        self.client.username_pw_set(user, password=password)  # set username and password
        self.client.connect(broker_address, port=port)  # connect to broker
        self.client.loop_start()  # start the loop
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect  # attach function to callback

        self.client.subscribe("#", 0)
        self.value = 0
        self.tiempo = 0
        self.amp = 0
        self.bat = 0
        self.pin1 = 0
        self.pin2 = 0
        self.pin3 = 0
        self.pin4 = 0
        self.pin5 = 0

        self.fase = 0
        self.var = 0
        self.vari = 1

        while self.Connected != True:
            while True:
                time.sleep(.01)   #REVISAR ESTE VALOR
                if self.vari == 0:
                    break

    def on_connect(self, client, userdata, flags, rc):
        if self.var == 0:
            if rc == 0:
                print("Connected to broker: CMQTT_prueba_HMI")
                self.Connected = True
                self.var = 1
            else:
                print("Connection failed")

    def on_message(self, client, obj, msg):
        global frec, tiempo_inicial, parar

        if msg.topic == "fecha":
            self.thefecha = msg.payload
        if msg.topic == "valor":
            if self.vari == 1:
                # print(msg.topic + " " + str(msg.payload))
                self.v_tiempo.append(float(msg.payload.decode('UTF-8').split(",")[0]))
                self.v_amp.append(float(msg.payload.decode('UTF-8').split(",")[1]))
                self.v_fase.append(float(msg.payload.decode('UTF-8').split(",")[2]))
                self.v_bat.append(float(msg.payload.decode('UTF-8').split(",")[3]))
                self.v_pin1.append(float(msg.payload.decode('UTF-8').split(",")[4]))
                self.v_pin2.append(float(msg.payload.decode('UTF-8').split(",")[5]))
                self.v_pin3.append(float(msg.payload.decode('UTF-8').split(",")[6]))
                self.v_pin4.append(float(msg.payload.decode('UTF-8').split(",")[7]))
                self.v_pin5.append(float(msg.payload.decode('UTF-8').split(",")[8]))

                self.save_data(self.thefecha)

        if msg.topic == "fin":
            self.save_data(self.thefecha)
            self.v_tiempo = []
            self.v_amp = []
            self.v_fase = []
            self.v_bat = []
            self.v_pin1 = []
            self.v_pin2 = []
            self.v_pin3 = []
            self.v_pin4 = []
            self.v_pin5 = []

            # self.client.disconnect()
            # self.client.loop_stop()
            self.vari = 0

    def save_data(self, lafecha):
        path = r'C:\Users\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\\' + lafecha + '.csv'
        with open(path, 'w') as fp:
            a = csv.writer(fp, delimiter=';')
            self.v_1 = array('f', np.array(self.v_tiempo))
            self.v_2 = array('f', np.array(self.v_amp))
            self.v_3 = array('f', np.array(self.v_fase))
            self.v_4 = array('f', np.array(self.v_bat))
            self.v_5 = array('f', np.array(self.v_pin1))
            self.v_6 = array('f', np.array(self.v_pin2))
            self.v_7 = array('f', np.array(self.v_pin3))
            self.v_8 = array('f', np.array(self.v_pin4))
            self.v_9 = array('f', np.array(self.v_pin5))


            k = 0
            a.writerows([['Tiempo', 'Dif(amp)', 'Dif(fase)', 'GND', 'Dif_2(fase)', 'Dif_2(amp)', 'Dif_1(fase)', 'Dif_1(amp)', 'Volt_Bat']])
            for step in self.v_1:
                a.writerows([[self.v_1[k], self.v_2[k], self.v_3[k], self.v_4[k], self.v_5[k], self.v_6[k], self.v_7[k], self.v_8[k], self.v_9[k]]])
                k = k + 1

if __name__=='__main__':
    General()
