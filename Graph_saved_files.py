from matplotlib import pyplot as plt
from numpy import genfromtxt
import numpy as np
import wx

def onButton(event):
    print "Button pressed."
app = wx.App()
frame = wx.Frame(None, -1, 'win.py')
frame.SetDimensions(0, 0, 200, 50)
# Create open file dialog
openFileDialog = wx.FileDialog(frame, "Open", "", "", "CSV files (*.csv)|*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
openFileDialog.ShowModal()
print(openFileDialog.GetPath())
openFileDialog.Destroy()

#Leer archivo
x = genfromtxt(openFileDialog.GetPath(), delimiter=';')
my_data_volts = np.delete(x, 0, 0)
print(my_data_volts)

# CAMBIAR ESTE NUMERO PARA SELECCIONAR EL PIN A GRAFICAR!!!!!
Pin = 1
x = my_data_volts[:,0]
plt.xlabel('Tiempo (s)')


if Pin==1:
    plt.ylabel('Pin1 (V)')
    plt.title('Pin 1')
    y = my_data_volts[:,1]
    labell = 'Pin 1'
if Pin==2:
    plt.ylabel('Pin2 (V)')
    plt.title('Pin 2')
    y = my_data_volts[:, 2]
    labell = 'Pin 2'
if Pin==3:
    plt.ylabel('Pin3 (V)')
    plt.title('Pin 3')
    y = my_data_volts[:, 3]
    labell = 'Pin 3'
if Pin==4:
    plt.ylabel('Pin4(V)')
    plt.title('Pin 4')
    y = my_data_volts[:, 4]
    labell = 'Pin 4'
if Pin==5:
    plt.plot(my_data_volts[:,0], my_data_volts[:,1], label='Pin 1')
    plt.plot(my_data_volts[:,0], my_data_volts[:,2], label='Pin 2')
    plt.plot(my_data_volts[:,0], my_data_volts[:,3], label='Pin 3')
    y = my_data_volts[:,4]
    labell = 'Pin 4'




plt.plot(y, label='error')

# plt.plot(x, y, label=labell)

plt.legend()
plt.show()

