'''
Codigo para el envio de mensajes al servidor en la comunicacion entre el pc y la rpi

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

import paho.mqtt.client as mqttClient
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker: CMQTT_mensaje")
        global Connected
        Connected = True
    else:
        print("Connection failed")

Connected = False

def envio(ArgT, ArgM):
    broker_address = "m12.cloudmqtt.com"
    port = 17785
    user = "qsbfmyfp"
    password = "zWnhGsM6YoH7"
    client = mqttClient.Client("CMQTT_mensaje")  # create new instance
    client.username_pw_set(user, password=password)  # set username and password
    client.connect(broker_address, port=port)  # connect to broker
    client.loop_start()  # start the loop
    # self.client.on_message = self.on_message
    client.on_connect = on_connect  # attach function to callback

    client.subscribe("#", 0)

    while Connected != True:
        time.sleep(.1)
    try:
        client.publish(ArgT, ArgM)
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print('Error al enviar el mensaje')

    client.disconnect()
    client.loop_stop()