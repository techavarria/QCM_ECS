'''
Junta los datos de amplitud y frecuencia leidos del servidor
con los datos de temperatura que se obtienen del modulo termoelectrico

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

import numpy as np
import csv
from numpy import genfromtxt


class Merge_it(object):

    def __init__(self, thedate):
        if thedate == 'delete':
            print('cambie el nombre de name = main')
        else:
            x = genfromtxt('C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\\' + thedate + '.csv', delimiter=';')
            my_data_volts = np.delete(x, 0, 0)
            y = genfromtxt('C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Resp_Sistema_' + thedate + '.csv', delimiter=';')
            my_data_temp = np.delete(y, 0, 0)
            if my_data_volts[3, -1] == 0:
                self.diferencial = 1
            else:
                self.diferencial = 0
            TempArray = []
            for i in range(len(my_data_volts[:, 0])):
                idx = self.find_nearest(my_data_temp[:, 0], my_data_volts[i, 0])
                TempArray.append([my_data_temp[idx, 2]])
            TempArray = np.array(TempArray)
            Final_array = np.append(my_data_volts, TempArray, 1)
            self.save_array(Final_array, thedate)

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    def save_array(self, array, thedate):
        if self.diferencial == 0:
            path = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Merged_' + thedate + '.csv'
            with open(path, 'w') as fp:
                a = csv.writer(fp, delimiter=';')
                a.writerows([['Tiempo', 'Dif(amp)x', 'Dif(fase)x', 'Dif(amp)y', 'Dif(fase)y', 'Dif(fase)', 'Dif(amp)', 'Dif(amp) calibrado', 'Dif(fase) calibrado', 'Temperatura']])
                for step in range(len(array[:,0])):
                    a.writerows([[array[step,0], array[step,1], array[step,2], array[step,3], array[step,4], array[step,5], array[step,6], array[step,7], array[step,8], array[step,9]]])
        elif self.diferencial == 1:
            path2 = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Merged_' + thedate + '.csv'
            with open(path2, 'w') as fp:
                b = csv.writer(fp, delimiter=';')
                b.writerows([['Tiempo', 'pin1', 'pin2', 'pin3', 'pin4', 'Temperatura']])
                for step in range(len(array[:, 0])):
                    b.writerows(
                        [[array[step, 0], array[step, 1], array[step, 2], array[step, 3], array[step, 4], array[step, 9]]])

if __name__=='__main__':
    Merge_it('23_04_2019-12.28.49')