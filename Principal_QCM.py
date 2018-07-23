import time
import threading
import CMQTT_read_RPi
import HMI_TEM_CMQTT_Freq

def fun_cmqtt():
    print("Se ejecuta la funcion CMQTT")
    CMQTT_read_RPi.General()

def fun_hmi():
    print("Se ejecuta la funcion HMI")
    HMI_TEM_CMQTT_Freq.main()

t = time.time()
t1 = threading.Thread(target=fun_hmi)
t2 = threading.Thread(target=fun_cmqtt)
t1.start()
t2.start()
t1.join()
t2.join()

print('Duracion: ' + str(time.time()-t))
quit()