#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 ************************************************************************************************
 *
 *  SISTEMA DE IDENTIFICACIÓN Y CONTROL PLANTA DE TEMPERATURA
 *
 *  Uniersidad EIA Grupo de investigación GIBEC
 *
 *  E-mail: tomas.echavarria@eia.edu.co
 *
 *----------------------------------------------------------------------------------------------
 *
 *  Archivo:        HMI_TEM_CMQTT_Freq.py
 *
 *  Version python: 2.7
 *
 *  Programador:    Lucas Tobon Vanegas
 *                  lucas.tobon.v@gmail.com
 *                  Tomas Echavarria Bayter
 *                  tomas.echavarria@eia.edu.co
 *
 *  Descripción:    Este archivo contiene los prototipos de funciones, tareas, variables,
 *                  definiciones, tipos de datos y constantes de la interfaz grafica
 *
 *  Creado:         Thu Jul 21 09:58:23 2016
 *
 *  Historia:       21.07.2016 - Estructura general de codigo clases y funciones
 *                  26.07.2016 - Comentarios y correccion de errores ejecución
 *                  23.07.2018 - Modificaciones y terminación del programa
                                por: Tomas Echavarria
 *
 *  Pendiente:      Perfiles de temperatura
 *                  Leer datos
 *
 ************************************************************************************************
 *
"""
import wx
import wx.lib.intctrl
import wx.lib.mixins.listctrl  as  listmix
import os
import matplotlib
matplotlib.use('WXAgg')
import time as tim
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas1
import pylab
import csv
from array import array
import numpy as np
import serial.tools.list_ports
from sistema_lectura import SerialData as DataGen
import Registros_TE as R
import CMQTT_mensaje
import Freq_GUI
from matplotlib import pyplot as plt
from numpy import genfromtxt
import merge_files


TIEMPO_REFRESCAR_MS = 50
TASA_MUESTREO_MS = 50                           # no se usa
RANGO_AUTOMATICO_X = 20000/TASA_MUESTREO_MS     # no se usa
RANGO_AUTOMATICO_Y = 100
RANGO_AUTOMATICO_Y_RPI = 5

tabla = [0, 0]

#----------------------------CLASE CONTROLES DE GRAFICA------------------------
class BoundControlBox(wx.Panel):

    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        self.value = initval
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, size=(35,-1),value=str(initval),style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    def is_auto(self):
        return self.radio_auto.GetValue()
    def manual_value(self):
        return self.value

class BoundControlBox2(wx.Panel):

    def __init__(self, parent, ID, label, initval_H, initval_L):
        wx.Panel.__init__(self, parent, ID)
        self.initval_H = initval_H
        self.initval_L = initval_L
        self.value_H = initval_H
        self.value_L = initval_L
        self.checked_H = False
        self.checked_L = False
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.check_H = wx.CheckBox(self, -1, label="Alto")
        self.check_L = wx.CheckBox(self, -1, label="Bajo")

        self.manual_H = wx.TextCtrl(self, -1, size=(35, -1), value=str(initval_H), style=wx.TE_PROCESS_ENTER)
        self.manual_L = wx.TextCtrl(self, -1, size=(35, -1), value=str(initval_L), style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_CHECKBOX, self.on_check_H, self.check_H)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_L, self.check_L)

        High_box = wx.BoxSizer(wx.HORIZONTAL)
        High_box.Add(self.check_H, flag=wx.ALIGN_CENTER_VERTICAL)
        High_box.Add(self.manual_H, flag=wx.ALIGN_CENTER_VERTICAL)

        Low_box = wx.BoxSizer(wx.HORIZONTAL)
        Low_box.Add(self.check_L, flag=wx.ALIGN_CENTER_VERTICAL)
        Low_box.Add(self.manual_L, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(High_box, 0, wx.ALL, 10)
        sizer.Add(Low_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)
    def on_check_H(self, event):
        if not self.checked_H:
            self.value_H = self.manual_H.GetValue()
            self.manual_H.Enable(self.checked_H)
        else:
            self.value_H = self.initval_H
            self.manual_H.Enable(self.checked_H)
        self.checked_H = not self.checked_H
    def on_check_L(self, event):
        if not self.checked_L:
            self.value_L = self.manual_L.GetValue()
            self.manual_L.Enable(self.checked_H)
        else:
            self.value_L = self.initval_L
            self.manual_L.Enable(self.checked_L)
        self.checked_L = not self.checked_L

#----------------------------CLASE SISTEMA DE ENTRADA--------------------------

class SystemInputBox(wx.Panel):

    def __init__(self, parent, ID, label, initval, minval, maxval):
        wx.Panel.__init__(self, parent, ID)
        self.value = initval
        box = wx.StaticBox(self, 0, label)
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.system_input = wx.lib.intctrl.IntCtrl(self,id=0,size=(50,20),value=initval,	min=minval,	max=maxval,	style=wx.TE_PROCESS_ENTER|wx.TE_CENTRE)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.system_input)
        sizer.Add(self.system_input, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
    def on_text_enter(self, event):
        if self.system_input.GetValue() >= self.system_input.GetMin() and self.system_input.GetValue() <= self.system_input.GetMax():
            self.value = self.system_input.GetValue()
            self.system_input.SelectAll()
    def step_value(self):
        return float(self.value)

#----------------------------CLASE SISTEMA DE SALIDA---------------------------

class SystemOutputBox(wx.Panel):

    def __init__(self,parent,label,val):
        wx.Panel.__init__(self,parent)
        box_1 = wx.StaticBox(self,0,label)
        sizer_1 = wx.StaticBoxSizer(box_1, wx.HORIZONTAL)
        self.system_output = wx.StaticText(self,size=(50,30),label= str(val),style=wx.TE_PROCESS_ENTER|wx.TE_CENTRE)
        sizer_1.Add(self.system_output, 5, wx.ALL, 10)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

#----------------------------CLASE GRAFICA PRINCIPAL--------------------------
# noinspection PyPackageRequirements

class PPLForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title = 'SISTEMA PARA EL CONTROL TERMICO Y MONITOREO DE PLANTA')
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.SetBackgroundColour('#E6E6E6')
        self.Maximize()
        #----------------ATRIBUTOS ESPECIALES DE CLASE-------------------------
        self.datagen = 0
        self.tiempo_step = [0.0]
        self.step     = [0.0] #SetPoint (entrada)
        self.sysresp  = [0.0] #Respuesta del sistema  Temp (entrada)
        self.actuador = [0.0] #Corriente del actuador (entrada)
        self.sysref   = [0.0] #Sensor de temp exterior
        self.tiempo_rpi = [0.0]
        self.amplitud_rpi = [0.0]
        self.fase_rpi = [0.0]
        self.paused = False
        self.run    = False
        self.setpp = 0      #SetPoint (salida)
        self.errors = [0.0] #Error (salida)

        self.tiempo_refresco = wx.Timer(self)
        self.tiempo_muestreo = wx.Timer(self)

        self.contador_tiempo = 0
        self.otravar = 0
        self.bandera = 0
        self.var_fin = 0
        self.num_en_tabla = 0
        self.detect_puerto = 0
        self.var_conect = 0
        self.var_listo = 0
        self.var_inicio = 0
        self.fecha_save = ''
        self.yaClickeo = 0
        #-------------------------METODOS--------------------------------------
        self.crear_menu_superior()
        self.grafo_1(0)
        self.crear_panel_principal()
        self.crear_barra_estado()
        self.tiempo_refresco.Start(TIEMPO_REFRESCAR_MS)
        self.tiempo_muestreo.Start(TASA_MUESTREO_MS)
        #-------------------------EVENTOS--------------------------------------
        self.Bind(wx.EVT_TIMER, self.on_tiempo_refresco, self.tiempo_refresco)
        self.Bind(wx.EVT_TIMER, self.on_tiempo_muestreo, self.tiempo_muestreo)

    def crear_menu_superior(self):
        self.menubar = wx.MenuBar()
        menu_file    = wx.Menu()
        menu_control = wx.Menu()
        self.menu_comunica = wx.Menu()
        menu_soporte = wx.Menu()

        #----------------INSTANCIAMIENTO y LAYOUTDE OBJETOS MENU FILE----------
        f_ggrafico = menu_file.Append(wx.ID_PRINT, u"&Guardar Gráfico\tCtrl-G", "Guarda gráfico en un archivo")
        f_gdatos   = menu_file.Append(wx.ID_SAVE, u"&Guardar Datos\tCtrl-D","Guarda datos en archivo")
        f_limpiar  = menu_file.Append(wx.ID_CLEAR, u"&Limpia Gráfico\tCtrl-L", "Limpia la grafica de señales")
        menu_file.AppendSeparator()
        f_exit = menu_file.Append(wx.ID_EXIT, "&Salir\tCtrl-Q","Salir")

        #---------------------EVENTOS DE COMPONENTES MENU FILE-----------------
        self.Bind(wx.EVT_MENU, self.on_save_plot, f_ggrafico)
        self.Bind(wx.EVT_MENU, self.on_save_data, f_gdatos)
        self.Bind(wx.EVT_MENU, self.on_limpiar_plot, f_limpiar)
        self.Bind(wx.EVT_MENU, self.OnClose, f_exit)

        #----------------INSTANCIAMIENTO y LAYOUTDE OBJETOS MENU CONTROL------
        c_tecnicas = menu_control.Append(wx.ID_INFO, u"&Tecnicas de control", "Seleccionar una tecnica de control")
        c_alarmas = menu_control.Append(wx.ID_INFO, u"&Alarmas", "Defina estado de alarmas")
        c_perfil = menu_control.Append(wx.ID_INFO, u"&Perfil de temperatura","Defina un perfil de temperatura")

        #---------------------EVENTOS DE COMPONENTES MENU CONTROL--------------
        self.Bind(wx.EVT_MENU, self.frametecnicas, c_tecnicas)
        self.Bind(wx.EVT_MENU, self.framealarmas, c_alarmas)

        #----------------INSTANCIAMIENTO y LAYOUTDE OBJETOS MENU COMUNICACIÓN------
        com_puerto = self.menu_comunica.Append(wx.ID_INFO, u"&Puerto Serial", "Seleccionar un puerto para la comunicación")
        com_conectar = self.menu_comunica.Append(wx.ID_INFO, u"&Conectar", "Seleccionar un puerto para la comunicación")

        #---------------------EVENTOS DE COMPONENTES MENU COMUNICACIÓN--------------
        self.menubar.Append(menu_file,"&ARCHIVO")
        self.menubar.Append(menu_control,"&CONTROL")
        self.menubar.Append(self.menu_comunica,u"&COMUNICACIÓN")
        self.menubar.Append(menu_soporte,"&SOPORTE")
        self.SetMenuBar(self.menubar)

    def crear_panel_principal(self):
        #-------------------INSTANCIAMIENTO DE OBJETOS-------------------------
        titulo_2 = wx.StaticText(self.panel, wx.ID_ANY, u'SISTEMA PARA EL CONTROL TERMICO Y MONITOREO DE PLANTA')
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        titulo_2.SetFont(font)

        self.canvas_1        = FigCanvas1(self.panel,wx.ID_ANY,self.fig_1)
        self.cid_up = self.canvas_1.mpl_connect('button_press_event', self.OnClick)
        self.cid_down = self.canvas_1.mpl_connect('button_release_event', self.OnRelease)

        titulo_3             = wx.StaticText(self.panel, wx.ID_ANY, u'PERFILES DE TEMPERATURA')
        titulo_3.SetFont(font)

        #-----------
        self.t_label         = wx.ComboBox(self.panel, wx.ID_ANY, choices=['T1','T2','T3'],value="",size=(100,50))
        self.t_temp          = SystemInputBox(self.panel, wx.ID_ANY,u"Temp °C",0,0,100)
        self.t_value         = SystemInputBox(self.panel, wx.ID_ANY, "Tiempo seg",0,0,100)
        self.t_grad          = SystemInputBox(self.panel, wx.ID_ANY, "Grad %",0,0,100)
        self.t_anadir        = wx.Button(self.panel, wx.ID_ANY,u"AÑADIR", size=(100,70))
        self.boton_iniciar   = wx.Button(self.panel, wx.ID_ANY,u"INICIAR", size=(100,40))
        self.ln              = wx.StaticLine(self.panel,wx.ID_ANY,wx.Point(1,0), wx.Size(1,470),wx.VERTICAL)
        self.boton_conectar  = wx.Button(self.panel, wx.ID_ANY, size=(100,70))
        self.boton_pausar    = wx.Button(self.panel, wx.ID_ANY, size=(100,70))
        self.xmax_control    = BoundControlBox(self.panel, wx.ID_ANY, u"X máx", 50)
        self.ymax_control    = BoundControlBox(self.panel, wx.ID_ANY, u"Y máx", 90)

        #---------------------------------------------------    # Agregué esto
        self.boton_parar = wx.Button(self.panel, wx.ID_ANY,u"PARAR", size=(100,40))

        self.t_label.Hide()
        self.t_temp.Hide()
        self.t_value.Hide()
        self.t_grad.Hide()
        self.t_anadir.Hide()

        self.index = 0
        self.list_ctrl = EditableListCtrl(self.panel,wx.ID_ANY, size=(-1, 100), style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.ALIGN_LEFT)

        self.list_ctrl.InsertColumn(0, '# pasos', width=50)
        self.list_ctrl.InsertColumn(1, 'Temp inicial', width=65)
        self.list_ctrl.InsertColumn(2, 'Duracion', width=65)

        btn = wx.Button(self.panel, label="+",style=wx.ALIGN_LEFT,size = (100, 40))
        btn2 = wx.Button(self.panel, label="Guardar",style=wx.ALIGN_LEFT,size = (100, 40))
        btn3 = wx.Button(self.panel, label='-',style=wx.ALIGN_LEFT,size = (100, 40))

        btn2.Hide()
        self.boton_pausar.Hide()
        btn.Bind(wx.EVT_BUTTON, self.add_line)
        btn2.Bind(wx.EVT_BUTTON, self.getColumn)
        btn3.Bind(wx.EVT_BUTTON, self.deleteRow)

        btn_frecuencia = wx.Button(self.panel, label="FRECUENCIA", style=wx.ALIGN_LEFT, size=(100,70))
        btn_frecuencia.Bind(wx.EVT_BUTTON, self.frecuencia)

        #--------------------------------------------
        self.o_grid          = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar Cuadrícula",style=wx.ALIGN_LEFT)
        self.o_setp          = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar Set Point",style=wx.ALIGN_LEFT)
        self.o_rsis          = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar R.Sistema",style=wx.ALIGN_LEFT)
        self.o_sctr          = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar S.Control",style=wx.ALIGN_LEFT)
        self.o_err           = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar Error",style=wx.ALIGN_LEFT)
        self.o_ref           = wx.CheckBox(self.panel, wx.ID_ANY, u"Ocultar Refer", style=wx.ALIGN_LEFT)

        self.l_step       = SystemOutputBox(self.panel, "Set Point ", 0)
        self.l_sysresp    = SystemOutputBox(self.panel, "R.Sistema", 0)
        self.l_actuador   = SystemOutputBox(self.panel, "S.Control", 0)
        self.l_errors     = SystemOutputBox(self.panel, "Error ", 0)
        self.l_sysref     = SystemOutputBox(self.panel, "Referencia ", 0)

        #---------------------EVENTOS DE COMPONENTES---------------------------
        self.Bind(wx.EVT_BUTTON,self.conectar,self.boton_conectar)
        self.Bind(wx.EVT_UPDATE_UI, self.act_estado_conectar, self.boton_conectar)

        self.Bind(wx.EVT_BUTTON, self.iniciar, self.boton_iniciar)
        self.Bind(wx.EVT_BUTTON, self.parar, self.boton_parar)

        self.Bind(wx.EVT_BUTTON, self.anadir, self.t_anadir)
        self.Bind(wx.EVT_BUTTON, self.pausar, self.boton_pausar)
        self.Bind(wx.EVT_UPDATE_UI, self.act_estado_pausar, self.boton_pausar)

        self.Bind(wx.EVT_CHECKBOX, self.on_o_grid, self.o_grid)
        self.Bind(wx.EVT_CHECKBOX, self.on_o_setp, self.o_setp)
        self.Bind(wx.EVT_CHECKBOX, self.on_o_rsis, self.o_rsis)
        self.Bind(wx.EVT_CHECKBOX, self.on_o_sctr, self.o_sctr)
        self.Bind(wx.EVT_CHECKBOX, self.on_o_err, self.o_err)
        self.Bind(wx.EVT_CHECKBOX, self.on_o_ref, self.o_ref)
        #-----------------------LAYOUT INTERFAZ--------------------------------
        PPSizer      = wx.BoxSizer(wx.VERTICAL)
        TituloSizer  = wx.BoxSizer(wx.HORIZONTAL)
        GraficaSizer = wx.BoxSizer(wx.HORIZONTAL)
        Input_Sizer  = wx.BoxSizer(wx.VERTICAL)

        botones_sizer = wx.BoxSizer(wx.HORIZONTAL)
        botones_sizer.Add(btn, 1, wx.ALL | wx.EXPAND, 5)
        botones_sizer.Add(btn3, 1, wx.ALL | wx.EXPAND, 5)

        inicio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        inicio_sizer.Add(self.boton_iniciar, 1, wx.ALL | wx.EXPAND, 5)
        inicio_sizer.Add(self.boton_parar, 1, wx.ALL | wx.EXPAND, 5)

        self.textarea = wx.TextCtrl(self, -1,style= wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 190))
        self.Bind(wx.EVT_LEFT_DOWN, self.clearTxtBox, self.textarea)

        ControlSizer = wx.BoxSizer(wx.HORIZONTAL)

        CheckSizer   = wx.BoxSizer(wx.VERTICAL)
        CheckSizer_2 = wx.BoxSizer(wx.VERTICAL)

        TituloSizer.Add(titulo_2, 0, wx.ALL, 5)

        Input_Sizer.Add(titulo_3,  0, wx.CENTER,5)
        Input_Sizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 10)
        Input_Sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        # Input_Sizer.AddSpacer(10)
        Input_Sizer.Add(botones_sizer, 0, wx.CENTER, 5)
        Input_Sizer.Add(self.t_label,  0, wx.CENTER, 5)
        Input_Sizer.Add(self.t_temp,   0, wx.CENTER, 5)
        Input_Sizer.Add(self.t_value,  0, wx.CENTER, 5)
        Input_Sizer.Add(self.t_grad,   0, wx.CENTER, 5)
        # Input_Sizer.AddSpacer(10)
        Input_Sizer.Add(self.t_anadir, 0, wx.CENTER, 5)
        Input_Sizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 10)
        Input_Sizer.Add(inicio_sizer, 0, wx.CENTER, 5)
        # Input_Sizer.AddSpacer(4)
        Input_Sizer.Add(self.textarea, 0, wx.CENTER|wx.EXPAND, 5)
        button_clear = wx.Button(self.panel, label='Borrar',size = (20, 20))
        button_clear.Bind(wx.EVT_BUTTON, self.clearTxtBox)
        Input_Sizer.Add(button_clear, 0, wx.ALL|wx.EXPAND, 10)
        # GraficaSizer.AddSpacer(10)
        GraficaSizer.Add(Input_Sizer)
        GraficaSizer.Add(self.ln, 0, wx.ALL, 5)
        GraficaSizer.Add(self.canvas_1, 0, wx.CENTER, 5)

        ControlSizer.Add(btn_frecuencia, 0, wx.ALL, 5)
        ControlSizer.Add(self.boton_conectar, 0, wx.ALL, 5)
        ControlSizer.Add(self.boton_pausar,   0, wx.ALL, 5)
        ControlSizer.Add(self.xmax_control,   0, wx.ALL, 5)
        ControlSizer.Add(self.ymax_control,   0, wx.ALL, 5)
        ControlSizer.Add(CheckSizer)
        ControlSizer.Add(CheckSizer_2)
        ControlSizer.Add(self.l_step,     0, wx.ALL, 5)
        ControlSizer.Add(self.l_sysresp,  0, wx.ALL, 5)
        ControlSizer.Add(self.l_actuador, 0, wx.ALL, 5)
        ControlSizer.Add(self.l_errors,   0, wx.ALL, 5)
        ControlSizer.Add(self.l_sysref,   0, wx.ALL, 5)

        CheckSizer.Add(self.o_grid,  0, wx.ALL, 5)
        CheckSizer.Add(self.o_setp, 0, wx.ALL, 5)
        CheckSizer.Add(self.o_rsis, 0, wx.ALL, 5)

        CheckSizer_2.Add(self.o_sctr, 0, wx.ALL, 5)
        CheckSizer_2.Add(self.o_err, 0, wx.ALL, 5)
        CheckSizer_2.Add(self.o_ref, 0, wx.ALL, 5)

        PPSizer.Add(TituloSizer, 0, wx.CENTER)
        PPSizer.Add(wx.StaticLine(self.panel, ), 0, wx.ALL|wx.EXPAND, 10)
        PPSizer.Add(GraficaSizer,0, wx.ALL|wx.CENTER, 5)
        PPSizer.Add(wx.StaticLine(self.panel, ), 0, wx.ALL|wx.EXPAND, 10)
        PPSizer.Add(ControlSizer, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        self.panel.SetSizer(PPSizer)
        PPSizer.Fit(self.panel)

    def clearTxtBox(self, event):
        self.textarea.Clear()

    def add_line(self, event):
        self.list_ctrl.InsertStringItem(self.index, str(self.index + 1))
        self.list_ctrl.SetStringItem(self.index, 1, "Grad")
        self.list_ctrl.SetStringItem(self.index, 2, "Seg")
        self.index += 1

    def getColumn(self, event):
        global tabla
        count = self.list_ctrl.GetItemCount()
        cols = self.list_ctrl.GetColumnCount()

        tabla = [[None]*cols]*count
        tabla = np.array(tabla)
        for row in range(count):
            for col in range(cols):
                ite = self.list_ctrl.GetItem(itemId=row, col=col)
                tabla[row,col] = (int(ite.GetText()))

    def deleteRow(self, e):
        count = self.list_ctrl.GetItemCount()
        self.list_ctrl.DeleteItem(count-1)
        self.index -= 1

    def frecuencia(self, e):
        Freq_GUI.Inicio()

    def OnClick(self, event):
        if self.yaClickeo == 1:
            self.fig_1.delaxes(event.inaxes)
            self.grafo_1(0)

        elif self.yaClickeo == 0:
            for i, ax in enumerate([self.axes, self.axes1, self.axes2, self.axes3]):
                if ax == event.inaxes:
                    self.clickenaxis(i)
                    self.yaClickeo = 1

    def OnRelease(self, event):
        pass

    def clickenaxis(self, axes_subplot):
        self.fig_1.delaxes(self.axes)
        self.fig_1.delaxes(self.axes1)
        self.fig_1.delaxes(self.axes2)
        self.fig_1.delaxes(self.axes3)

        self.grafo_1(axes_subplot + 1)

    def graf_axes1(self):
        x_label = 'Tiempo (m)'
        pylab.setp(self.axes.set_xlabel(x_label), fontsize=10)
        pylab.setp(self.axes.set_ylabel('Temperatura %'.decode('utf-8')), fontsize=10)
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plot_step = self.axes.plot(self.step, linewidth=1, color=(0, 0, 0), label='Set Point')[0]
        self.plot_sysresp = self.axes.plot(self.step, linewidth=1, color=(1, 0, 0), label='R.Sistema')[0]
        self.plot_actuador = self.axes.plot(self.step, linewidth=1, color=(1, 1, 0), label='S.Control')[0]
        self.plot_errors = self.axes.plot(self.step, linewidth=1, color=(1, 0, 1), label='Error')[0]
        self.plot_sysref = self.axes.plot(self.step, linewidth=1, color=(0, 1, 0), label='Referencia')[0]

        self.axes.legend(bbox_to_anchor=(1.0, 0.47), loc=1, frameon=False, labelspacing=0.3, prop={'size': 7})

    def graf_axes2(self):
        x_label = 'Tiempo (m)'
        pylab.setp(self.axes1.set_xlabel(x_label), fontsize=10)
        pylab.setp(self.axes1.set_ylabel('Amplitud %'.decode('utf-8')), fontsize=10)
        pylab.setp(self.axes1.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes1.get_yticklabels(), fontsize=8)

        self.plot_a_rpi = self.axes1.plot(self.step, linewidth=1, color=(0, 0, 0), label='Amplitud')[0]

        self.axes1.legend(bbox_to_anchor=(1.0, 0.2), loc=1, frameon=False, labelspacing=0.3, prop={'size': 7})

    def graf_axes3(self):
        x_label = 'Tiempo (m)'
        pylab.setp(self.axes2.set_xlabel(x_label), fontsize=10)
        pylab.setp(self.axes2.set_ylabel('Fase %'.decode('utf-8')), fontsize=10)
        pylab.setp(self.axes2.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes2.get_yticklabels(), fontsize=8)

        self.plot_f_rpi = self.axes2.plot(self.step, linewidth=1, color=(1, 0, 0), label='Fase')[0]

        self.axes2.legend(bbox_to_anchor=(1.0, 0.2), loc=1, frameon=False, labelspacing=0.3, prop={'size': 7})

    def graf_axes4(self):
        x_label = 'Tiempo (m)'
        pylab.setp(self.axes3.set_xlabel(x_label), fontsize=10)
        pylab.setp(self.axes3.set_ylabel('Temp,Amp,Fase %'.decode('utf-8')), fontsize=10)
        pylab.setp(self.axes3.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes3.get_yticklabels(), fontsize=8)

        self.plot_sysresp1 = self.axes3.plot(self.step, linewidth=1, color=(1, 0, 0), label='R.Sistema')[0]
        self.plot_a_rpi1 = self.axes3.plot(self.step, linewidth=1, color=(1, 0, 1), label='Amplitud')[0]
        self.plot_f_rpi1 = self.axes3.plot(self.step, linewidth=1, color=(1, 1, 0), label='Fase')[0]

        self.axes3.legend(bbox_to_anchor=(1.0, 0.35), loc=1, frameon=False, labelspacing=0.3, prop={'size': 7})

    def grafo_1(self, fueclick):
        if fueclick == 1:
            self.axes = self.fig_1.add_subplot(111)
            self.axes.set_axis_bgcolor('white')
            self.graf_axes1()

        elif fueclick == 2:
            self.axes1 = self.fig_1.add_subplot(111)
            self.axes1.set_axis_bgcolor('white')
            self.graf_axes2()

        elif fueclick == 3:
            self.axes2 = self.fig_1.add_subplot(111)
            self.axes2.set_axis_bgcolor('white')
            self.graf_axes3()

        elif fueclick == 4:
            self.axes3 = self.fig_1.add_subplot(111)
            self.axes3.set_axis_bgcolor('white')
            self.graf_axes4()

        else:
            if self.yaClickeo != 1:
                self.dpi = 100
                self.fig_1 = plt.figure(figsize=(12, 4.5), dpi=self.dpi)
                self.fig_1.set_facecolor('#E6E6E6')

            self.axes  = self.fig_1.add_subplot(221)
            self.axes.set_axis_bgcolor('white')

            self.axes1 = self.fig_1.add_subplot(222)
            self.axes1.set_axis_bgcolor('white')

            self.axes2 = self.fig_1.add_subplot(223)
            self.axes2.set_axis_bgcolor('white')

            self.axes3 = self.fig_1.add_subplot(224)
            self.axes3.set_axis_bgcolor('white')

            self.graf_axes1()
            self.graf_axes2()
            self.graf_axes3()
            self.graf_axes4()

            self.fig_1.subplots_adjust(left=0.09, right=0.85, top=0.96, bottom=0.1)
            self.yaClickeo = 0

    def crear_barra_estado(self):
        self.statusbar = self.CreateStatusBar()
        self.PushStatusText(u"Programa en Ejecución")

    def pint_graf(self):
        if self.xmax_control.is_auto():
            xmax = self.tiempo_step[-1] if self.tiempo_step[-1] > 0.5 else 0.5
        else:
            xmax = int(self.xmax_control.manual_value())

        if self.ymax_control.is_auto():
            ymax = self.sysresp[len(self.sysresp)-1] + 10 if self.sysresp[len(self.sysresp)-1] + 10 > RANGO_AUTOMATICO_Y else RANGO_AUTOMATICO_Y #Redimensiona la ventana cuando la señal supera el intervalo ymax inicial
        else:
            ymax = int(self.ymax_control.manual_value())

        xmax_rpi = self.tiempo_rpi[-1] if self.tiempo_rpi[-1] > 0.5 else 0.5
        ymax_rpi = self.amplitud_rpi[len(self.amplitud_rpi)-1] + 10 if self.amplitud_rpi[len(self.amplitud_rpi)-1] + 10 > RANGO_AUTOMATICO_Y_RPI else RANGO_AUTOMATICO_Y_RPI

        self.axes.set_xbound(lower=0, upper=xmax)
        self.axes.set_ybound(lower=0, upper=ymax)
        self.axes.grid(False) if self.o_grid.IsChecked() else self.axes.grid(True, color='gray') #Muestra cuadricula si el check esta activo
        pylab.setp(self.axes.get_xticklabels(), visible=True)

        self.axes1.set_xbound(lower=0, upper=xmax_rpi)
        self.axes1.set_ybound(lower=0, upper=5.5)
        self.axes1.grid(False) if self.o_grid.IsChecked() else self.axes1.grid(True,color='gray')  # Muestra cuadricula si el check esta activo
        pylab.setp(self.axes1.get_xticklabels(), visible=True)

        self.axes2.set_xbound(lower=0, upper=xmax_rpi)
        self.axes2.set_ybound(lower=0, upper=5.5)
        self.axes2.grid(False) if self.o_grid.IsChecked() else self.axes2.grid(True,color='gray')  # Muestra cuadricula si el check esta activo
        pylab.setp(self.axes2.get_xticklabels(), visible=True)

        self.axes3.set_xbound(lower=0, upper=xmax)
        self.axes3.set_ybound(lower=0, upper=ymax)
        self.axes3.grid(False) if self.o_grid.IsChecked() else self.axes3.grid(True,color='gray')  # Muestra cuadricula si el check esta activo
        pylab.setp(self.axes3.get_xticklabels(), visible=True)

        # Señal de setpoint
        if self.o_setp.IsChecked():
            self.plot_step.set_xdata([0])
            self.plot_step.set_ydata([0])
        else:
            self.plot_step.set_xdata(self.tiempo_step)
            self.plot_step.set_ydata(np.array(self.step))

        # Señal de respuesta del sistema
        if self.o_rsis.IsChecked():
            self.plot_sysresp.set_xdata([0])
            self.plot_sysresp.set_ydata([0])
            self.plot_sysresp1.set_xdata([0])
            self.plot_sysresp1.set_ydata([0])

        else:
            self.plot_sysresp.set_xdata(self.tiempo_step)
            self.plot_sysresp.set_ydata(np.array(self.sysresp))
            self.plot_sysresp1.set_xdata(self.tiempo_step)
            self.plot_sysresp1.set_ydata(np.array(self.sysresp))

        # Señal de control
        if self.o_sctr.IsChecked():
            self.plot_actuador.set_xdata([0])
            self.plot_actuador.set_ydata([0])
        else:
            self.plot_actuador.set_xdata(self.tiempo_step)
            self.plot_actuador.set_ydata(np.array(self.actuador))

        # Señal de error
        if self.o_err.IsChecked():
            self.plot_errors.set_xdata([0])
            self.plot_errors.set_ydata([0])
        else:
            self.plot_errors.set_xdata(self.tiempo_step)
            self.plot_errors.set_ydata(np.array(self.errors))

        if self.o_ref.IsChecked():
            self.plot_sysref.set_xdata([0])
            self.plot_sysref.set_ydata([0])
        else:
            self.plot_sysref.set_xdata(self.tiempo_step)
            self.plot_sysref.set_ydata(np.array(self.sysref))

        ## VECTOR TIEMPO
        self.plot_a_rpi.set_xdata(self.tiempo_rpi)
        self.plot_f_rpi.set_xdata(self.tiempo_rpi)
        self.plot_a_rpi1.set_xdata(self.tiempo_rpi)
        self.plot_f_rpi1.set_xdata(self.tiempo_rpi)

        self.plot_a_rpi.set_ydata(np.array(self.amplitud_rpi))
        self.plot_f_rpi.set_ydata(np.array(self.fase_rpi))
        self.plot_a_rpi1.set_ydata(np.array(self.amplitud_rpi))
        self.plot_f_rpi1.set_ydata(np.array(self.fase_rpi))

        try:
            self.canvas_1.draw()
        except:
            print('tiempo_step')
            print(len(self.tiempo_step))
            print('step')
            print(len(self.step))
            print('sysresp')
            print(len(self.sysresp))
            print('actuador')
            print(len(self.actuador))
            print('errors')
            print(len(self.errors))
            print('sysref')
            print(len(self.sysref))
            print('---')

        self.l_step.system_output.SetLabel(str(abs(self.step[-1])))
        self.l_sysresp.system_output.SetLabel(str(self.sysresp[-1]))
        self.l_actuador.system_output.SetLabel(str(self.actuador[-1]))
        self.l_errors.system_output.SetLabel(str(self.errors[-1]))
        self.l_sysref.system_output.SetLabel(str(self.sysref[-1]))

    def conectar(self,event):
        if (Freq_GUI.frecuencia == 0) and (Freq_GUI.fi == 0) and (Freq_GUI.fp == 0) and (Freq_GUI.ff == 0):
            print('Configure la frecuencia')
            self.textarea.AppendText('Configure la frecuencia\r\n')
        else:
            if self.var_listo == 0:
                if os.name == 'nt' and list(serial.tools.list_ports.comports()):
                    p_disponibles = list(serial.tools.list_ports.comports())
                    # puerto = p_disponibles[0][0]
                    # print(puerto)                     # para revisar cual puerto es
                    for l in range(len(p_disponibles)):
                        if 'Prolific' in p_disponibles[l][1]:
                            puerto = p_disponibles[l][0]
                            self.detect_puerto = 1

                    if ((self.detect_puerto == 1) and (self.var_conect == 0)):
                        self.datagen = DataGen(puerto)
                        self.var_conect = 1

                    if self.detect_puerto == 0:
                        print('Conecte el modulo termoelectrico')
                        self.textarea.AppendText('Conecte el modulo termoelectrico\r\n')
                    else:
                        try:
                            v_prueba = float(self.datagen.next('$R0?\r'))
                            self.run = not self.run
                            self.var_listo = 1
                            self.boton_conectar.SetLabel('CONECTADO')
                            self.fecha_save = tim.strftime("%d_%m_%Y-%H.%M.%S")
                            path = r'C:\Users\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\\' + self.fecha_save + '.csv'
                            with open(path, 'w') as fp:
                                a = csv.writer(fp, delimiter=';')
                                a.writerows([['Tiempo', 'Amplitud', 'Fase']])
                                a.writerows([[0, 0, 0]])
                        except:
                            print('Encienda el modulo termoelectrico')
                            self.textarea.AppendText('Encienda el modulo termoelectrico\r\n')
                else:
                    wx.MessageBox(u"NO HAY DISPOSITIVOS CONECTADOS", "Info", style=wx.CENTER|wx.OK|wx.ICON_ERROR)
                self.eje_tiempo = tim.time()
            else:
                print('Ya esta conectado')
                self.textarea.AppendText('Ya esta conectado\r\n')

    def act_estado_conectar(self, event):
        if self.run == True:
            label = "CONECTADO"
        else:
            label = "CONECTAR"
        self.boton_conectar.SetLabel(label)

    def iniciar(self, event):
        if self.var_inicio == 0:
            if self.var_listo == 1:
                global tabla
                count = self.list_ctrl.GetItemCount()
                cols = self.list_ctrl.GetColumnCount()
                tabla = [[None] * cols] * count
                tabla = np.array(tabla)
                for row in range(count):
                    for col in range(cols):
                        ite = self.list_ctrl.GetItem(itemId=row, col=col)
                        try:
                            tabla[row, col] = (int(ite.GetText()))
                        except:
                            pass

                if (len(tabla)) > 0:
                    tabla1 = np.delete(tabla, 0, 1)
                    if None in tabla1:
                        self.num_en_tabla = 1
                        print('Escriba valores validos en la tabla')
                        self.textarea.AppendText('Escriba valores validos en la tabla\r\n')
                    else:
                        self.num_en_tabla = 0

                if count < 1:
                    print('Error: Agregue una fila')
                    self.textarea.AppendText('Error: Agregue una fila\r\n')

                if ((count > 0) and (self.num_en_tabla == 0)):
                    CMQTT_mensaje.envio('fecha', self.fecha_save)
                    if Freq_GUI.unicaobarrido == 1:
                        CMQTT_mensaje.envio('inicio', str(Freq_GUI.frecuencia))
                    elif Freq_GUI.unicaobarrido == 2:
                        CMQTT_mensaje.envio('barrido', (str(Freq_GUI.fi) + ',' + str(Freq_GUI.fp) + ',' + str(Freq_GUI.ff)))
                    if self.paused == True:
                        self.paused = False

                    self.eje_tiempo = tim.time()
                    self.var_inicio = 1
                    self.ind_pasos = 0

                    self.datagen.next('$R16=1\r')
                    self.datagen.next('$R23=1\r')
                    self.datagen.next('$R13=5\r')  # Probar con 4 o 6 Pi o Pid
                    self.datagen.next('$R0=' + str(tabla[0, 1]) + '\r')
                    self.datagen.next('$W\r')
                    self.contador_tiempo = tim.time()
                    self.bandera = 1

                    self.duracion = np.zeros(tabla.shape[0])
                    for t in range(int(tabla.shape[0])):
                        if t == 0:
                            self.duracion[0] = tabla[0, 2]
                        else:
                            self.duracion[t] = tabla[t, 2] + self.duracion[t-1]
                    print(self.duracion)
            else:
                print('Conectese al modulo termoelectrico')
                self.textarea.AppendText('Conectese al modulo termoelectrico\r\n')
        else:
            print('Espere que el perfil termine o hunda el boton PARAR')
            self.textarea.AppendText('Espere que el perfil termine o hunda el boton PARAR\r\n')
    def parar(self, event):
        if self.var_listo == 1:
            self.paused = True
            self.bandera = 0
            self.tiempo_step = [0.0]
            self.step = [0.0]
            self.sysresp = [0.0]
            self.actuador = [0.0]
            self.sysref = [0.0]
            self.errors = [0.0]
            self.tiempo_rpi = [0.0]
            self.amplitud_rpi = [0.0]
            self.fase_rpi = [0.0]

            self.plot_actuador.set_xdata([0])
            self.plot_errors.set_xdata([0])
            self.plot_step.set_xdata([0])
            self.plot_sysref.set_xdata([0])
            self.plot_sysresp.set_xdata([0])
            self.plot_sysresp1.set_xdata([0])
            self.plot_a_rpi.set_xdata([0])
            self.plot_a_rpi1.set_xdata([0])
            self.plot_f_rpi.set_xdata([0])
            self.plot_f_rpi1.set_xdata([0])

            self.pint_graf()

            if self.var_inicio == 1:
                self.datagen.next('$Q\r')
                CMQTT_mensaje.envio('fin', self.fecha_save)

            self.var_inicio = 0
        else:
            print('Dar inicio primero')
            self.textarea.AppendText('Dar inicio primero\r\n')

    def anadir(self, event):
        app = wx.App(False)
        frame = MyForm()
        frame.Show()
        app.MainLoop()

    def pausar(self, event):
        self.paused = not self.paused

    def act_estado_pausar(self, event):
        label = "REANUDAR" if self.paused==True else "PAUSAR"
        self.boton_pausar.SetLabel(label)

    def on_o_grid(self, event):
        self.pint_graf()

    def on_o_setp(self, event):
        self.pint_graf()

    def on_o_rsis(self, event):
        self.pint_graf()

    def on_o_sctr(self, event):
        self.pint_graf()

    def on_o_err(self, event):
        self.pint_graf()

    def on_o_ref(self, event):
        self.pint_graf()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png|SVG (*.svg)|*.svg"
        dlg = wx.FileDialog(self,message="Guardar gáfico como...",	defaultDir=os.getcwd(),defaultFile=("Grafico_Resp_Sistema_"+self.fecha_save), wildcard=file_choices, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        # if dlg.ShowModal() == wx.ID_OK:       ### DESCOMENTAR PARA PREGUNTAR SI QUIERE GUARDAR
        if (dlg.GetFilterIndex() == 0):
            dlg.SetFilename(dlg.GetFilename() + ".png")
        else:
            dlg.SetFilename(dlg.GetFilename() + ".svg")
        path = dlg.GetPath()
        path = r'C:\Users\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Grafico_Resp_Sistema_' + self.fecha_save + '.png'

        self.canvas_1.print_figure(path, dpi=self.dpi*6)#3Resolucion de imagen
        # self.flash_status_message("Guardado en %s" % path)

    def on_save_data(self, event):
        tiempo_step1 = []
        step1       = []
        sysrep1     = []
        actuador1   = []
        errors1     = []
        sysref1     = []
        ind_zero = 0
        j = 0

        while ind_zero == 0:
            if self.step[j] != 0:
                ind_zero = j
            j += 1
        # print(ind_zero)
        # # print('step ' + str(self.step))
        # # print('ind_zeros ' + str(ind_zero))
        # print(self.tiempo_step)
        for i in range(len(self.tiempo_step) - ind_zero):

            # if self.step[i + ind_zero] != self.step[ind_zero]:
            step1.append(self.step[i + ind_zero])
            tiempo_step1.append(self.tiempo_step[i + ind_zero])
            sysrep1.append(self.sysresp[i + ind_zero])
            sysref1.append(self.sysref[i + ind_zero])
            actuador1.append(self.actuador[i + ind_zero])
            errors1.append(self.errors[i + ind_zero])

        tiempo_step2 = [x - tiempo_step1[0] for x in tiempo_step1]
        tiempo_step3 = [x * 60 for x in tiempo_step2]

        file_choices = "CSV (*.csv)|*.csv"

        # dlg = wx.FileDialog(self,message="Guardar datos como...",defaultDir=os.getcwd(),defaultFile=tim.strftime('Resp_Sistema_'+"%H.%M.%S--%d_%m_%Y"),wildcard=file_choices,style=wx.SAVE)
        dlg = wx.FileDialog(self,message="Guardar datos como...",defaultDir=os.getcwd(),defaultFile=('Resp_Sistema_' + self.fecha_save),wildcard=file_choices,style=wx.SAVE)

        # if dlg.ShowModal() == wx.ID_OK:           ### DESCOMENTAR PARA PREGUNTAR SI QUIERE GUARDAR
        # path = dlg.GetPath()
        path = r'C:\Users\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Resp_Sistema_' + self.fecha_save + '.csv'
        with open(path, 'w') as fp:
            a = csv.writer(fp, delimiter=';')

            v_tiemp  = array('f', np.array(tiempo_step3 ))
            setps    = array('f', np.array(step1        ))
            rsiss    = array('f', np.array(sysrep1      ))
            sctrs    = array('f', np.array(actuador1    ))
            errs     = array('f', np.array(errors1      ))
            refs     = array('f', np.array(sysref1      ))

            k = 0
            a.writerows([['Tiempo (ms)','Escalon','Respuesta','Actuador','Error','Referencia']])#,'Perturbacion']])
            for step in setps:
                a.writerows([[v_tiemp[k],setps[k],rsiss[k],sctrs[k],errs[k],refs[k]]])#,pers[k]]])
                k=k+1
        # self.flash_status_message("Guardado en %s" % path)

    def on_limpiar_plot(self, event):
        self.step     = [0.0]
        self.sysresp  = [0.0]
        self.actuador = [0.0]
        self.errors   = [0.0]
        self.sysref   = [0.0]

    def on_tiempo_refresco(self, event):                            # Cuenta el tiempo para los perfiles
        global tabla
        if not self.paused and self.run:
            self.pint_graf()

        if (self.bandera == 1):
            print(tim.time()-self.contador_tiempo)
            self.num_pasos = int(tabla.shape[0])

            if (tim.time() - self.contador_tiempo > self.duracion[self.ind_pasos]):
                self.ind_pasos += 1
                if self.ind_pasos == self.num_pasos:
                    self.otravar = 1
                else:
                    self.datagen.next('$R16=1\r')
                    self.datagen.next('$R23=1\r')
                    self.datagen.next('$R13=5\r')
                    self.datagen.next('$R0=' + str(tabla[self.ind_pasos, 1]) + '\r')
                    self.datagen.next('$W\r')

        if (self.otravar == 1) and (self.var_fin == 0):

            CMQTT_mensaje.envio('fin', self.fecha_save)
            self.datagen.next('$Q\r')
            self.var_fin = 1
            self.bandera = 0
            self.paused = True

            self.on_save_data(self)
            self.on_save_plot(self)
            # open files to merge:
            merge_files.Merge_it(self.fecha_save)       # junta datos de amp y fase con temperatura

            self.Close()

        # ---------------------------------------------------------------------------------------------------------------

    def on_tiempo_muestreo(self, event):
        if not self.paused and self.run:
            try:
                #### cargar csv
                x = genfromtxt(
                    'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\\' + self.fecha_save + '.csv',
                    delimiter=';')
                my_data_volts = np.delete(x, 0, 0)

                tiempo_rp = my_data_volts[-1, 0]
                amplitud_rp = my_data_volts[-1, 1]
                fase_rp = my_data_volts[-1, 2]

                if self.bandera == 1:
                    v_step = float(self.datagen.next('$R0?\r'))
                    v_sysresp = float(self.datagen.next('$R100?\r'))
                    v_actuador = float(self.datagen.next('$R106?\r'))
                    v_sysref = float(self.datagen.next('$R102?\r'))

                    self.step.append(v_step)
                    self.sysresp.append(v_sysresp)
                    self.actuador.append(v_actuador)
                    self.errors.append(abs(v_sysresp - v_step) * 100 / v_step)
                    self.sysref.append(v_sysref)  # Sensor de temperatura 3 (externo)

                    vec_long = [len(self.step), len(self.sysresp), len(self.actuador), len(self.errors), len(self.sysref)]
                    val_min = min(vec_long)
                    self.step = self.step[0:val_min]
                    self.sysresp = self.sysresp[0:val_min]
                    self.actuador = self.actuador[0:val_min]
                    self.errors = self.errors[0:val_min]
                    self.sysref = self.sysref[0:val_min]

                    if (val_min == len(self.tiempo_step)+1):
                        self.tiempo_step.append((tim.time() - self.eje_tiempo) / 60)

                    self.tiempo_rpi.append(tiempo_rp / 60)
                    self.amplitud_rpi.append(amplitud_rp)
                    self.fase_rpi.append(fase_rp)

            except:
                print('hubo error de comunicación, se ignoró el dato')

    def flash_status_message(self, msg, flash_len_ms=1000):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_flash_status_off, self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)

    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def OnClose(self, event):
        result = wx.MessageBox(u"¿Seguro quieres salir?","Info", style=wx.CENTER|wx.YES_NO|wx.ICON_QUESTION)

        if result == wx.NO:
            print("No Salio")
        else:
            print("Salio")
            print(self.datagen.next('$Q\r'))
            self.datagen.__del__()
            CMQTT_mensaje.envio('fin', self.fecha_save)

            StrFecha = tim.strftime("%H.%M.%S--%d_%m_%Y")
            flagSave = 0
            exit()

    def frametecnicas(self, event):
        frame_2 = Control()
        frame_2.Show()

    def framealarmas(self, event):
        frame_3 = Alarmas(self.datagen)
        frame_3.Show()

class Control(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="RUTINA DE CONTROL / MOTOERES PASO A PASO")
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        title = wx.StaticText(self.panel_2, wx.ID_ANY, u"CONTROL MANUAL DESPLAZAMIENTO Y SELECCIÓN")

        # Variables

        # Seleccionar motores / Check Buttons
        # Seleccionar Velocidad / Text
        # Seleccionar Pasos / Text
        # Seleccionar Direccion ComboBox
        # Boton de START-STOP-PAUSE / Button
        # Mostrar la posición de los motores / Gauge

        self.CH_Motor1 = wx.CheckBox(self.panel_2, wx.ID_ANY, "M1(SELECCIONAR)")
        self.CH_Motor2 = wx.CheckBox(self.panel_2, wx.ID_ANY, "M2(DESPLAZAR)")

        vel = wx.StaticText(self.panel_2, wx.ID_ANY, "VEL: ")
        way = wx.StaticText(self.panel_2, wx.ID_ANY, "DIR: ")
        step = wx.StaticText(self.panel_2, wx.ID_ANY, "STP: ")

        self.txt_vel = wx.TextCtrl(self.panel_2)
        self.txt_dir = wx.TextCtrl(self.panel_2)
        self.txt_step = wx.TextCtrl(self.panel_2)

        B_Start = wx.Button(self.panel_2, wx.ID_ANY, "START", size=(200, 50))
        B_Stop = wx.Button(self.panel_2, wx.ID_ANY, "STOP", size=(200, 50))

        # EVENTOS
        self.Bind(wx.EVT_BUTTON, self.start, B_Start)
        self.Bind(wx.EVT_BUTTON, self.stop, B_Stop)

        # SIZERS
        PPSizer_2 = wx.BoxSizer(wx.VERTICAL)

        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        TxtSizer = wx.BoxSizer(wx.HORIZONTAL)
        CHSizer = wx.BoxSizer(wx.HORIZONTAL)

        ButtonSizer.Add(B_Start, 0, wx.CENTRE, 5)
        ButtonSizer.Add(B_Stop, 0, wx.CENTRE, 5)

        TxtSizer.Add(vel, 0, wx.CENTRE, 5)
        TxtSizer.Add(self.txt_vel, 0, wx.CENTRE, 5)
        TxtSizer.Add(way, 0, wx.CENTRE, 5)
        TxtSizer.Add(self.txt_dir, 0, wx.CENTRE, 5)
        TxtSizer.Add(step, 0, wx.CENTRE, 5)
        TxtSizer.Add(self.txt_step, 0, wx.CENTRE, 5)

        CHSizer.Add(self.CH_Motor1, 0, wx.CENTRE, 5)
        CHSizer.AddSpacer(20)
        CHSizer.Add(self.CH_Motor2, 0, wx.CENTRE, 5)

        PPSizer_2.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer_2.Add(title, 0, wx.CENTRE, 5)
        PPSizer_2.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer_2.Add(CHSizer, 0, wx.CENTRE, 5)
        PPSizer_2.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer_2.Add(TxtSizer, 0, wx.CENTRE, 5)
        PPSizer_2.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer_2.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer_2.Add(ButtonSizer, 0, wx.CENTRE, 5)

        self.panel_2.SetSizer(PPSizer_2)
        PPSizer_2.Fit(self)

    def start(self, event):
        pass

    def stop(self, event):
        pass

class Alarmas(PPLForm):

    def __init__(self,datagen):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="RUTINA DE CONTROL / MOTOERES PASO A PASO")
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        title = wx.StaticText(self.panel_2, wx.ID_ANY, u"CONTROL MANUAL DESPLAZAMIENTO Y SELECCIÓN")
        self.datagen = datagen
        self.voltagein = BoundControlBox2(self.panel_2, wx.ID_ANY, u"Voltage In", 0,50)
        self.voltageout = BoundControlBox2(self.panel_2, wx.ID_ANY, u"Corriente Out", 0,50)

        self.fan1current = BoundControlBox2(self.panel_2, wx.ID_ANY, u"I Ventilador 1", 0,50)
        self.fan2current = BoundControlBox2(self.panel_2, wx.ID_ANY, u"I Ventilador 2", 0,50)

        self.t1 = BoundControlBox2(self.panel_2, wx.ID_ANY, u"T1", 0,50)
        self.t2 = BoundControlBox2(self.panel_2, wx.ID_ANY, u"T2", 0,50)
        self.t3 = BoundControlBox2(self.panel_2, wx.ID_ANY, u"T3", 0,50)
        self.t4 = BoundControlBox2(self.panel_2, wx.ID_ANY, u"T4", 0,50)

        self.send_button = wx.Button(self.panel_2, wx.ID_ANY, u"ENVIAR", size=(100, 40))
        self.read_button = wx.Button(self.panel_2, wx.ID_ANY, u"LEER", size=(100, 40))

        # EVENTOS
        self.Bind(wx.EVT_BUTTON, self.enviar, self.send_button)
        self.Bind(wx.EVT_BUTTON, self.leer, self.read_button)

        # SIZERS
        PPSizer = wx.BoxSizer(wx.VERTICAL)

        voltage = wx.BoxSizer(wx.HORIZONTAL)
        fan = wx.BoxSizer(wx.HORIZONTAL)
        temp = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.BoxSizer(wx.HORIZONTAL)

        voltage.Add(self.voltagein, 0, wx.CENTRE, 5)
        voltage.Add(self.voltageout, 0, wx.CENTRE, 5)

        fan.Add(self.fan1current, 0, wx.CENTRE, 5)
        fan.Add(self.fan2current, 0, wx.CENTRE, 5)

        temp.Add(self.t1, 0, wx.CENTRE, 5)
        temp.Add(self.t2, 0, wx.CENTRE, 5)
        temp.Add(self.t3, 0, wx.CENTRE, 5)
        temp.Add(self.t4, 0, wx.CENTRE, 5)

        button.Add(self.send_button, 0, wx.CENTRE, 5)
        button.Add(self.read_button, 0, wx.CENTRE, 5)

        PPSizer.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer.Add(title, 0, wx.CENTRE, 5)
        PPSizer.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer.Add(voltage, 0, wx.CENTRE, 5)
        PPSizer.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer.Add(fan, 0, wx.CENTRE, 5)
        PPSizer.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer.Add(temp, 0, wx.CENTRE, 5)
        PPSizer.Add(wx.StaticLine(self.panel_2, ), 0, wx.ALL | wx.EXPAND, 5)
        PPSizer.Add(button, 0, wx.CENTRE, 5)

        self.panel_2.SetSizer(PPSizer)
        PPSizer.Fit(self)

    def enviar(self, event):

        if self.voltagein.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'ALVH', self.voltagein.manual_H.GetValue()))
        if self.voltagein.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'ALVL', self.voltagein.manual_L.GetValue()))

        if self.voltageout.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'ALMCH', self.voltageout.manual_H.GetValue()))
        if self.voltageout.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'ALMCL', self.voltageout.manual_L.GetValue()))

        if self.fan1current.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'ALF1CH', self.fan1current.manual_H.GetValue()))
        if self.fan1current.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'ALF1CL', self.fan1current.manual_L.GetValue()))

        if self.fan2current.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'ALF2CH', self.fan2current.manual_H.GetValue()))
        if self.fan2current.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'ALF2CL', self.fan2current.manual_L.GetValue()))

        if self.t1.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'AT1H', self.t1.manual_H.GetValue()))
        if self.t1.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'AT1L', self.t1.manual_L.GetValue()))

        if self.t2.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'AT2H', self.t2.manual_H.GetValue()))
        if self.t2.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'AT2L', self.t2.manual_L.GetValue()))

        if self.t3.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'AT3H', self.t3.manual_H.GetValue()))
        if self.t3.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'AT3L', self.t3.manual_L.GetValue()))

        if self.t4.check_H.GetValue():
            self.datagen.next(R.com('Escribir', 'AT4H', self.t4.manual_H.GetValue()))
        if self.t4.check_L.GetValue():
            self.datagen.next(R.com('Escribir', 'AT4L', self.t4.manual_L.GetValue()))

    def leer(self, events):

        self.voltagein.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALVH')))))   #str(float(self.datagen.next('$R45?\r'))))
        self.voltagein.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALVL')))))

        self.voltageout.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALMCH')))))
        self.voltageout.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALMCL')))))

        self.fan1current.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALF1CH')))))
        self.fan1current.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALF1CL')))))

        self.fan2current.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALF2CH')))))
        self.fan2current.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'ALF1CL')))))

        self.t1.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT1H')))))
        self.t1.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT1L')))))

        self.t2.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT2H')))))
        self.t2.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT2L')))))

        self.t3.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT3H')))))
        self.t3.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT3L')))))

        self.t4.manual_H.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT4H')))))
        self.t4.manual_L.SetValue(str(float(self.datagen.next(R.com('Leer', 'AT4L')))))

#-----------------Clases importadas de Perfiles.py------------------------

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Perfiles de Temperatura")
        panel = wx.Panel(self, wx.ID_ANY)


def main():
    app = wx.App(False)

    frame = PPLForm()
    frame.Show()

    app.MainLoop()

if __name__ == "__main__":
    main()