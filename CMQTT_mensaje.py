import paho.mqtt.client as mqttClient
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker: CMQTT_mensaje")
        global Connected  # Use global variable
        Connected = True  # Signal connection
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
    # ----
    client.subscribe("#", 0)

    while Connected != True:
        time.sleep(.1)
        # print(Connected)
    try:
        client.publish(ArgT, ArgM)
        # print('envio')
        # break
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print('Error al enviar el mensaje')
    # print('ciclo1')
    client.disconnect()
    client.loop_stop()