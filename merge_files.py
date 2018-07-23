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
        # path = dlg.GetPath()
        path  = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Merged_' + thedate + '.csv'
        with open(path, 'w') as fp:
            a = csv.writer(fp, delimiter=';')
            # v_tie = array('f', (array[:,0]))
            # v_a = array('f', (array[:,1]))
            # v_f = array('f', (array[:,2]))
            # v_tem = array('f', (array[:,3]))
            a.writerows([['Tiempo', 'Amplitud', 'Fase', 'Temperatura']])

            for step in range(len(array[:,0])):
                a.writerows([[array[step,0], array[step,1], array[step,2], array[step,3]]])

if __name__=='__main__':
    Merge_it('delete')