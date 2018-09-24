'''
Interfaz grafica para cuadrar la frecuencia o barrido de frecuencias de la tarjeta generadora de senales

Autor: Tomas Echavarria - tomas.echavarria@eia.edu.co
'''

import serial
import time
import FTW_Freq_calc
import ser as seri
import wx
import os
import csv
import ctypes  # An included library with Python install.

frecuencia = 0
unicaobarrido = 0
fi = 0
fp = 0
ff = 0
class Ventana(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Control de NCO")
        # print(seri.serial_ports())
        self.ser = serial.Serial(seri.serial_ports()[0], 9600, timeout=0.01, parity=serial.PARITY_EVEN, rtscts=0)
        # print(seri.serial_ports()[0])
        self.mostrado = 0
        self.Interfaz()
        # wx.Frame(wx.ID_ANY, 'control NCO')

    def Interfaz(self):

        self.panel = wx.Panel(self, wx.ID_ANY)

        menuBar = wx.MenuBar()
        fileButton = wx.Menu()
        guardarItem = fileButton.Append(wx.ID_SAVE, 'Guardar registros', 'No se que es esto')
        exitItem = fileButton.Append(wx.ID_EXIT, 'Salir', 'status msg...')
        menuBar.Append(fileButton, '&Archivo')
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.Quit, exitItem)
        self.Bind(wx.EVT_MENU, self.Save, guardarItem)

        #####
        labelTitle = wx.StaticText(self.panel, wx.ID_ANY, 'Seleccione una opcion')
        labelOne = wx.StaticText(self.panel, wx.ID_ANY, 'Frecuencia:')
        self.inputTxtOne = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        labelTwo = wx.StaticText(self.panel, wx.ID_ANY, 'Frec. inicial:')
        self.inputTxtTwo = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        labelThree = wx.StaticText(self.panel, wx.ID_ANY, 'Frec. paso:')
        self.inputTxtThree = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        labelFour = wx.StaticText(self.panel, wx.ID_ANY, 'Frec. final:')
        self.inputTxtFour = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        labelRate = wx.StaticText(self.panel, wx.ID_ANY, 't en cada f (s, max 10ms)')
        self.inputRate = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        ##### PARA MODO CHIRP DE AD9854 DESCOMENTAR
        labelRate.Hide()
        self.inputRate.Hide()
        #####
        btn_get = wx.Button(self.panel, label="Leer registros")
        btn_set = wx.Button(self.panel, label="Ajustar frecuencia")
        btn_set_sweep = wx.Button(self.panel, label="Hacer barrido")
        btn_chirp = wx.Button(self.panel, label="Chirp")

        btn_get.Bind(wx.EVT_BUTTON, self.Reg_read)
        btn_set.Bind(wx.EVT_BUTTON, self.SetFreq)
        btn_set_sweep.Bind(wx.EVT_BUTTON, self.SetSweep)
        btn_chirp.Bind(wx.EVT_BUTTON, self.SetChirp)

        btn_chirp.Hide()
        #####
        topSizer = wx.BoxSizer(wx.VERTICAL)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputFourSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputRateSizer = wx.BoxSizer(wx.HORIZONTAL)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        inputOneSizer.Add(labelOne, 0, wx.ALL, 5)
        inputOneSizer.Add(self.inputTxtOne, 1, wx.ALL | wx.EXPAND, 5)
        inputOneSizer.Add(btn_set, 0, wx.ALL, 5)
        inputTwoSizer.Add(labelTwo, 0, wx.ALL, 5)
        inputTwoSizer.Add(self.inputTxtTwo, 1, wx.ALL | wx.EXPAND, 5)
        inputThreeSizer.Add(labelThree, 0, wx.ALL, 5)
        inputThreeSizer.Add(self.inputTxtThree, 1, wx.ALL | wx.EXPAND, 5)
        inputFourSizer.Add(labelFour, 0, wx.ALL, 5)
        inputFourSizer.Add(self.inputTxtFour, 1, wx.ALL | wx.EXPAND, 5)
        inputRateSizer.Add(labelRate, 0, wx.ALL, 5)
        inputRateSizer.Add(self.inputRate, 1, wx.ALL | wx.EXPAND, 5)

        btnSizer.Add(btn_set_sweep, 0, wx.ALL, 5)
        btnSizer.Add(btn_chirp, 0, wx.ALL, 5)

        topSizer.Add(labelTitle, 0, wx.ALIGN_CENTER, 5)
        topSizer.Add(wx.StaticLine(self.panel, ), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(inputOneSizer, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_MULTILINE, 5)
        topSizer.Add(wx.StaticLine(self.panel, ), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Barrido de Frecuencias'), 0, wx.ALIGN_CENTER, 5)

        topSizer.Add(inputTwoSizer, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_MULTILINE, 5)
        topSizer.Add(inputThreeSizer, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_MULTILINE, 5)
        topSizer.Add(inputFourSizer, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_MULTILINE, 5)
        topSizer.Add(inputRateSizer, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_MULTILINE, 5)

        # topSizer.Add(btn_set_sweep, 0, wx.ALIGN_CENTER, 5)
        topSizer.Add(btnSizer, 0, wx.ALIGN_CENTER, 5)

        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        # topSizer.Add(btnSizer, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(btn_get, 0, wx.ALL | wx.CENTER, 5)

        self.topSizer = topSizer

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.SetTitle('Control NCO')

    def Quit(self, e):
        self.Close()

    def Save(self, e):
        try:
            # self.Reg_Frec

            file_choices = "CSV (*.csv)|*.csv"
            dlg = wx.FileDialog(self, message="Guardar datos como...", defaultDir=os.getcwd(),
                                defaultFile=time.strftime('Registros_' + "%H.%M.%S--%d_%m_%Y"), wildcard=file_choices,
                                style=wx.SAVE)

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                with open(path, 'w') as fp:
                    a = csv.writer(fp, delimiter=';')

                    a.writerows([['R. Generales', 'R. Frecuencia']])

                    k = 0
                    for step in self.Reg_Frec:
                        if k >= len(self.Reg_Generales):
                            a.writerows([['XX', self.Reg_Frec[k]]])
                        else:
                            a.writerows([[self.Reg_Generales[k], self.Reg_Frec[k]]])
                        k = k + 1
        except:
            ctypes.windll.user32.MessageBoxA(0, 'Lea primero los registros', 'ERROR', 1)

    def Reg_read(self, event):
        buena_comu = 1
        while buena_comu == 1:
            self.ser.write('01'.decode("hex"))
            time.sleep(1)
            print('a')
            a = self.ser.read(self.ser.inWaiting())
            print('b')
            print('length')
            print(len(a))
            if len(a) == 31: #> 0: # para que siempre cumpla
                a = a.split(',')
                a[len(a) - 1] = a[len(a) - 1][0:2]
                self.Reg_Generales = a[0:4]
                self.Reg_Frec = a[4:]
                print('Registros Generales')
                print(self.Reg_Generales)
                print('Regsitros de Frecuencia')
                print(self.Reg_Frec)

                str_stxt = "Registros Generales\n" + str(self.Reg_Generales) + '\nRegistros de Frecuencia\n' + str(self.Reg_Frec)
                self.stxt = wx.StaticText(self.panel, wx.ID_ANY, str_stxt)
                self.topSizer.Add(self.stxt, 0, wx.ALL | wx.EXPAND, 5)

                self.panel.SetSizer(self.topSizer)
                self.topSizer.Fit(self)
                self.SetTitle('Control NCO')

                if self.mostrado == 1:
                    self.topSizer.Hide(12)
                    self.topSizer.Remove(12)
                    self.panel.SetSizer(self.topSizer)
                    self.topSizer.Fit(self)
                    self.SetTitle('Control NCO')

                self.mostrado = 1
                buena_comu = 0
                # Agregar para leer otros registros

    def SetFreq(self, event):
        global frecuencia, unicaobarrido
        if self.inputTxtOne.GetValue() == '':
            frecuencia = 0
        else:
            frecuencia = int(self.inputTxtOne.GetValue())
            unicaobarrido = 1

        self.Close()


    def SetSweep(self, event):
        # Para barrido
        global unicaobarrido, fi, fp, ff
        if (self.inputTxtTwo.GetValue() == '') or (self.inputTxtThree.GetValue() == '') or (self.inputTxtFour.GetValue() == ''):
            fi = 0
            fp = 0
            ff = 0
        else:
            fi = int(self.inputTxtTwo.GetValue())
            fp = int(self.inputTxtThree.GetValue())
            ff = int(self.inputTxtFour.GetValue())
            unicaobarrido = 2
        self.Close()

    def SetChirp(self, event):
        # Para chirp
        self.ser.write('03'.decode("hex"))

        frecu = int(self.inputTxtTwo.GetValue())
        FTW_hex = FTW_Freq_calc.FTW_calc(frecu)
        self.ser.write(FTW_hex.decode("hex"))

        frec_p = int(self.inputTxtThree.GetValue())
        print(frec_p)
        FTW_hex = FTW_Freq_calc.FTW_calc(frec_p)
        self.ser.write(FTW_hex.decode("hex"))

        t_en_f = float(self.inputRate.GetValue())
        N_hex = FTW_Freq_calc.ramp_rate(t_en_f)
        self.ser.write(N_hex.decode("hex"))

        frec_f = int(self.inputTxtFour.GetValue())

        Num_pasos = ((frec_f-frecu)/frec_p)*t_en_f
        Np_hex = FTW_Freq_calc.update_rate(Num_pasos)
        self.ser.write(Np_hex.decode("hex"))

def Inicio():
    app = wx.App(False)
    frame = Ventana()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    Inicio()