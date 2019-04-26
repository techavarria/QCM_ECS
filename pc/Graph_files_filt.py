from matplotlib import pyplot as plt
from numpy import genfromtxt
import numpy as np
import plotly
import plotly.graph_objs as go
import os.path
from scipy import signal
from scipy.fftpack import fft

class graficar(object):

    def __init__(self, thedate):

        self.thedate = thedate
        x = genfromtxt(
            'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\\Merged_' + thedate + '.csv',
            delimiter=';')
        self.my_data_volts = np.delete(x, 0, 0)

        for d in range(10): #elimina los primeros 10 datos
            self.my_data_volts = np.delete(self.my_data_volts, 0, 0)

        for i in range(2):
            if i == 0:
                nombre = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Fase_' + thedate
                self.graficar1(nombre, i+1)
                # pass
            if i == 1:
                # pass
                nombre = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Amp_' + thedate
                self.graficar1(nombre, i+1)

    def graficar1(self, nombregrafica, tipodegraf):      # tipodegraf # 1 para fase, 2 para amplitud

        # Funciones
        def filtro(t, s, fc):

            # FFT
            N = len(t)
            T = t[1]-t[0]
            y = s
            yf = fft(y)
            xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
            yff = 2.0 / N * np.abs(yf[0:N // 2])

            tr2 = go.Scatter(x=xf, y=yff, name='FFT', marker=dict(color='orange'))
            dat2 = [tr2]
            layout = go.Layout(title='fft sin filtro', xaxis=dict(), yaxis=dict(showticklabels=True, titlefont=dict(color='blue'), tickfont=dict(color='blue')))
            nombre = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\FFT'
            n = 1
            while os.path.isfile(nombre + '.html'):
                nombre = nombre + '_(' + str(n) + ')'
                n += 1
            fig2 = go.Figure(data=dat2, layout=layout)
            # plotly.offline.plot(fig2, filename=nombre + '.html')


            T = np.mean(np.diff(t))
            fs = 1/(T)
            print(fs)
            #################################
            # Filter

            # w = fc / (fs / 2.0)  # Normalize the frequency
            # w = 40/fs
            w = fc #0.00334
            b, a = signal.butter(5, w, 'low')
            output = signal.filtfilt(b, a, s)

            trace1 = go.Scatter(x=t, y=s, name='Original', marker=dict(color='blue'))
            trace2 = go.Scatter(x=t, y=output, name='Filtrada', yaxis='y2', marker=dict(color='orange'))

            data = [trace1, trace2]

            layout = go.Layout(
                title=self.titulo,
                # width=1800,
                xaxis=dict(
                    # showticklabels=True,
                    domain=[0.03, 0.94]
                ),
                yaxis=dict(
                    # title='Voltios',
                    showticklabels=True,
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    # title='yaxis2 title',
                    showticklabels=True,
                    titlefont=dict(color='orange'),
                    tickfont=dict(color='orange'),
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=0.0
                )
            )
            nombre = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\Filtro'
            n = 1
            while os.path.isfile(nombre + '.html'):
                nombre = nombre + '_(' + str(n) + ')'
                n += 1
            fig = go.Figure(data=data, layout=layout)
            # plotly.offline.plot(fig, filename=nombre + '.html')

            # FFT
            N = len(t)
            T = t[1] - t[0]
            x = t
            y = output
            yf = fft(y)
            xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
            yff = 2.0 / N * np.abs(yf[0:N // 2])

            tr2 = go.Scatter(x=xf, y=yff, name='FFT', marker=dict(color='orange'))
            dat2 = [tr2]
            layout = go.Layout(title='fft filtrada', xaxis=dict(),
                               yaxis=dict(showticklabels=True, titlefont=dict(color='blue'),
                                          tickfont=dict(color='blue')))
            nombre = 'C:\Users\\tomas.echavarria\Documents\Investigacion\HMI_modificado\Datos\CMQTT\FFT_filtrada'
            n = 1
            while os.path.isfile(nombre + '.html'):
                nombre = nombre + '_(' + str(n) + ')'
                n += 1
            fig2 = go.Figure(data=dat2, layout=layout)
            # plotly.offline.plot(fig2, filename=nombre + '.html')

            return output
        def diferencia():

            self.tiempo = self.tiempo[:-1]
            self.y_dif = self.y2 - self.y

            trace1 = go.Scatter(x=self.tiempo, y=self.y, name='D(X)',
                                marker=dict(color='blue'))
            trace2 = go.Scatter(x=self.tiempo, y=self.y2, name='D(F)', yaxis='y2',
                                marker=dict(color='orange'))
            trace3 = go.Scatter(x=self.tiempo, y=self.y_dif, name='D_dig', yaxis='y3',
                                marker=dict(color='green'))
            trace4 = go.Scatter(x=self.tiempo, y=self.y4, name='Temp (C)', yaxis='y4',
                                marker=dict(color='red'))

            trace1_1 = go.Scatter(x=self.tiempo, y=(self.y - np.mean(self.y)), name='D(X)',
                                marker=dict(color='blue'))
            trace2_1 = go.Scatter(x=self.tiempo, y=(self.y2 - np.mean(self.y2)), name='D(F)',
                                marker=dict(color='orange'))
            trace3_1 = go.Scatter(x=self.tiempo, y=(self.y_dif - np.mean(self.y_dif)), name='D_dig',
                                marker=dict(color='green'))

            data = [trace1, trace2, trace3, trace4]
            data_1 = [trace1_1, trace2_1, trace3_1, trace4]

            layout = go.Layout(
                title='Diferencia en ' + self.titulo,
                # width=1800,
                xaxis=dict(
                    # showticklabels=True,
                    domain=[0.03, 0.94]
                ),
                yaxis=dict(
                    # title='Voltios',
                    showticklabels=True,
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    # title='yaxis2 title',
                    showticklabels=True,
                    titlefont=dict(color='orange'),
                    tickfont=dict(color='orange'),
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=0.0
                ),
                yaxis3=dict(
                    # title='yaxis4 title',
                    showticklabels=True,
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                    anchor='x',
                    overlaying='y',
                    side='right'
                ),
                yaxis4=dict(
                    # title='yaxis5 title',
                    showticklabels=True,
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=1
                )
            )
            fig = go.Figure(data=data, layout=layout)
            fig_1 = go.Figure(data=data_1, layout=layout)

            nombre = nombregrafica + '_Dif'
            nombre_1 = nombregrafica + '_Dif_centrada'

            n = 1
            while os.path.isfile(nombre + '.html'):
                nombre = nombre + '_(' + str(n) + ')'
                n += 1
            m = 1
            while os.path.isfile(nombre_1 + '.html'):
                nombre_1 = nombre_1 + '_(' + str(m) + ')'
                m += 1


            plotly.offline.plot(fig, filename=nombre + '.html')
            plotly.offline.plot(fig_1, filename=nombre_1 + '.html')
        def graph(num, centrada):

            if num==1:
                nombre = nombregrafica
            else:
                nombre = nombregrafica + '_Filtered'
                self.y = self.y_filt
                self.y2 = self.y2_filt
                self.y3 = self.y3_filt
                self.y4 = self.y4_filt

            if centrada:
                print('entro')
                nombre = nombre + '_Centrada'
                self.y -= np.mean(self.y)
                self.y2 -= np.mean(self.y2)
                self.y3 -= np.mean(self.y3)
                trace2 = go.Scatter(x=self.tiempo, y=self.y2, name=self.n2, marker=dict(color='orange'))
                trace3 = go.Scatter(x=self.tiempo, y=self.y3, name=self.n3, marker=dict(color='green'))
            else:
                nombre = nombregrafica
                trace2 = go.Scatter(x=self.tiempo, y=self.y2, name=self.n2, yaxis='y2', marker=dict(color='orange'))
                trace3 = go.Scatter(x=self.tiempo, y=self.y3, name=self.n3, yaxis='y3', marker=dict(color='green'))
            n = 1
            while os.path.isfile(nombre + '.html'):
                nombre = nombre + '_(' + str(n) + ')'
                n += 1

            trace1 = go.Scatter(x=self.tiempo, y=self.y, name=self.n1, marker=dict(color='blue'))
            trace4 = go.Scatter(x=self.tiempo, y=self.y4, name='Temp (C)', yaxis='y4', marker=dict(color='red'))

            data = [trace1,trace2,trace3,trace4]

            layout = go.Layout(
                title=self.titulo,
                # width=1800,
                xaxis=dict(
                    # showticklabels=True,
                    title='min',
                    domain=[0.03, 0.94]
                ),
                yaxis=dict(
                    title='V',
                    showticklabels=True,
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    # title='yaxis2 title',
                    showticklabels=True,
                    titlefont=dict(color='orange'),
                    tickfont=dict(color='orange'),
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=0.0
                ),
                yaxis3=dict(
                    # title='yaxis4 title',
                    showticklabels=True,
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                    anchor='x',
                    overlaying='y',
                    side='right'
                ),
                yaxis4=dict(
                    # title='yaxis5 title',
                    showticklabels=True,
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=1
                )
            )
            fig = go.Figure(data=data, layout=layout)
            plotly.offline.plot(fig, filename=nombre + '.html')

        #################################
        # Inicio
        lim_i = 0
        lim_fin = -1  # -1 es el ultimo valor
        x = self.my_data_volts[lim_i:lim_fin, 0]/60
        plt.xlabel('Tiempo (s)')
        self.tiempo = x

        if tipodegraf == 1:
            self.titulo = 'Diferencia de Fase'
            self.y = self.my_data_volts[lim_i:lim_fin, 2]
            self.n1 = 'Dif(F)x (V)'
            self.y2 = self.my_data_volts[lim_i:lim_fin, 4]
            self.n2 = 'Dif(F)y (V)'
            self.y3 = self.my_data_volts[lim_i:lim_fin, 5]
            self.n3 = 'Dif(F) (V)'
        if tipodegraf == 2:
            self.titulo = 'Diferencia de Amplitud'
            self.y = self.my_data_volts[lim_i:lim_fin, 1]
            self.n1 = 'Dif(Amp)x (V)'
            self.y2 = self.my_data_volts[lim_i:lim_fin, 3]
            self.n2 = 'Dif(Amp)y (V)'
            self.y3 = self.my_data_volts[lim_i:lim_fin, 6]
            self.n3 = 'Dif(Amp) (V)'
        self.y4 = self.my_data_volts[lim_i:lim_fin, 9]

        # Filtros
        self.y_filt = filtro(self.tiempo, self.y, 0.00334)
        self.y2_filt = filtro(self.tiempo, self.y2, 0.00334)
        self.y3_filt = filtro(self.tiempo, self.y3, 0.00334)
        self.y4_filt = filtro(self.tiempo, self.y4, 0.00334)

        # Graficas
        # graph(1, False)    # Senal sin filtrar, sin centrar
        graph(1, True)    # Senal sin filtrar, centrada
        # diferencia()    # hacer resta de senales digitalmente para comarar con resta analoga
        # graph(2)    # Senal filtrada

if __name__ == '__main__':
    print('cambie name = main')
    # graficar('09_04_2019-09.30.19')
    # graficar('09_04_2019-09.58.47')
    # graficar('09_04_2019-14.07.54')
    # graficar('10_04_2019-09.55.18')
    # graficar('09_04_2019-14.40.47')
