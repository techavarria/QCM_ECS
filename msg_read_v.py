import paho.mqtt.client as mqttClient
import time
import ads1256
import csv
from array import array
import numpy as np
import urllib
import commands

import ser as seri
import serial
import FTW_Freq_calc
import SetFrequency
import multiprocessing
status_connected = False
while status_connected == False:
    try:
        url = 'https://www.google.com'
        urllib.urlopen(url)
        status_connected = True
    except:
        status_connected = False


gain = 1  # ADC's Gain parameter
sps = 25  # ADC's SPS parameter
AllChannelValuesVolts = [0, 0, 0, 0, 0, 0, 0, 0]
AllChannelValues = [0, 0, 0, 0, 0, 0, 0, 0]
ads1256.start(str(gain), str(sps))

frec = 0
fi = 0
fp = 0
ff = 0
tiempo_incial = 0
parar = 0

v_value = [0]
v_tiempo = [0]
v_amp = [0]
v_fase = [0]
var_fech = 0
fecha = ''
var_setfrec = 1

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
        client.publish('RPi', 'Conectado y listo, IP: ' + commands.getoutput('hostname -I'))
    else:
        print("Connection failed")

def on_message(client, obj, msg):
    global frec, tiempo_inicial, parar, var_fech, fecha, var_setfrec, fi, fp, ff
    if msg.topic == 'fecha':
        fecha = msg.payload
        var_fech = 1
    if msg.topic == 'reboot':
        commands.getoutput('sudo reboot')
    if msg.topic == 'IP':
        client.publish("IP Address", commands.getoutput('hostname -I'))
    if var_fech == 1:

        if msg.topic == "inicio":
            frec = float(msg.payload.decode('UTF-8'))
            tiempo_inicial = time.time()
            parar = 0
            var_setfrec = 0

        if msg.topic == "barrido":
            fi = int(msg.payload.decode('UTF-8').split(",")[0])
            fp = int(msg.payload.decode('UTF-8').split(",")[1])
            ff = int(msg.payload.decode('UTF-8').split(",")[2])
            tiempo_inicial = time.time()
            parar = 0
            var_setfrec = 3
            client.publish("elmensaje", msg.payload)
            client.publish("fi", fi)

        if msg.topic == "fin":
            parar = 1


def save_data():
    # path = r'/home/pi/Documents/' + time.strftime("%d_%m_%Y-%H.%M.%S") + '.csv'
    path = r'/home/pi/Documents/' + fecha + '.csv'
    with open(path, 'w') as fp:
        a = csv.writer(fp, delimiter=';')
        v_value.pop(0)
        v_tiempo = [0]
        v_amp = [0]
        v_fase = [0]
        v_1 = [0]
        v_2 = [0]
        v_3 = [0]
        for i in (v_value):
            v_tiempo.append(float(str(i).split(",")[0]))
            v_amp.append(float(str(i).split(",")[1]))
            v_fase.append(float(str(i).split(",")[2]))

        v_1 = array('f', np.array(v_tiempo))
        v_2 = array('f', np.array(v_amp))
        v_3 = array('f', np.array(v_fase))

        k = 0
        a.writerows([['Tiempo', 'Amplitud', 'Fase']])
        for step in v_1:
            a.writerows([[v_1[k], v_2[k], v_3[k]]])
            k = k + 1




Connected = False  # global variable for the state of the connection

broker_address = "m12.cloudmqtt.com"
port = 17785
user = "qsbfmyfp"
password = "zWnhGsM6YoH7"

client = mqttClient.Client("RPi3")  # create new instance
client.username_pw_set(user, password=password)  # set username and password
client.on_connect = on_connect  # attach function to callback
client.connect(broker_address, port=port)  # connect to broker

client.on_message = on_message

client.loop_start()  # start the loop

client.subscribe("#", 0)

value = 0
amp = 0
fase = 0
tiempo = 0
v_i = 0
while Connected != True:  # Wait for connection
    time.sleep(0.01)
try:
    while True:
        if (frec != 0) or (fi != 0) or (fp != 0) or (ff != 0):
            if var_setfrec == 0:
                t1 = multiprocessing.Process(target=SetFrequency.fun_setFreq, args=(frec,))
                t1.start()
                var_setfrec = 2
                # Podria hacer que el pic envie un mensaje cuando se ponga la frecuencia y leerlo para cambiar un avariable
                # O se podrian leer los registros para ver si si se puso la frecuencia que se queria
            if var_setfrec == 3:
                t2 = multiprocessing.Process(target=SetFrequency.fun_setSweep, args=(fi,fp,ff,))
                t2.start()
                var_setfrec = 2
                # Podria hacer que el pic envie un mensaje cuando se ponga la frecuencia y leerlo para cambiar un avariable
                # O se podrian leer los registros para ver si si se puso la frecuencia que se queria
            if var_setfrec == 2:
                AllChannelValues = ads1256.read_all_channels()
                for i in range(0, 8):
                    AllChannelValuesVolts[i] = (((AllChannelValues[i] * 100) / 167.0) / int(gain)) / 1000000.0

                amp = AllChannelValuesVolts[1]
                fase = AllChannelValuesVolts[0]
                tiempo = time.time() - tiempo_inicial
                value = str(tiempo) + ',' + str(amp) + ',' + str(fase)

                client.publish("valor", value)
                v_value.append(value)
        if parar == 1:
            t3 = multiprocessing.Process(target=SetFrequency.fun_setFreq, args=(0,))
            if ('t1' in locals()) or ('t1' in globals()):
                t1.terminate()
            if ('t2' in locals()) or ('t2' in globals()):
                t2.terminate()
            t3.start()
            frec = 0
            fi = 0
            fp = 0
            ff = 0
            save_data()
            v_value = [0]
            var_fech = 0
            parar = 0
            tiempo = 0
            amp = 0
            fase = 0
        time.sleep(.01)  # revisar si toca aumentar este valor

except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()
ads1256.stop()
