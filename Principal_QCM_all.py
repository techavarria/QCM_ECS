'''
Codigo inicial para realizar las pruebas de las microbalanzas de quarzo

Crea dos hilos para ejecutar codigos diferentes al mismo tiempo

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

import time
import threading
import CMQTT_read_RPi_all
import HMI_TEM_CMQTT_Freq_all

def fun_cmqtt():
    print("Se ejecuta la funcion CMQTT")
    CMQTT_read_RPi_all.General()

def fun_hmi():
    print("Se ejecuta la funcion HMI")
    HMI_TEM_CMQTT_Freq_all.main()

t = time.time()
t1 = threading.Thread(target=fun_hmi)
t2 = threading.Thread(target=fun_cmqtt)
t1.start()
t2.start()
t1.join()
t2.join()

print('Duracion: ' + str(time.time()-t))
quit()