import plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import colorlover as cl
import cufflinks as cf

from graphics.hydrogram_biuld import HydrogramBiuld


class HydrogramParcial(HydrogramBiuld):

    def __init__(self, data, peaks, threshold, title, threshold_criterion=None):
        super().__init__()
        self.data = data
        self.peaks = peaks
        self.threshold = threshold
        self.threshold_criterion = threshold_criterion
        self.title = title

    def plot(self, type_criterion):
        bandxaxis = go.XAxis(
            title="Data",
        )

        bandyaxis = go.YAxis(
            title="Vazão(m³/s)",
        )

        try:
            if self.threshold_criterion is None:
                raise AttributeError

            name = 'Hidrograma Série de Duração Parcial - %s' % self.title
            layout = dict(
                title = name,
                showlegend=True,
                width=1890, height=827,
                xaxis=bandxaxis,
                yaxis=bandyaxis,
                font=dict(family='Time New Roman', size=34, color='rgb(0,0,0)'))

            data = []
            data.append(self._plot_one(self.data))
            data.append(self._plot_threshold())
            data.append(self._plot_threshold_criterion(type_criterion))
            data += self._plot_event_peaks()

            aux_name = name.replace(' - ', '_')
            aux_name2 = aux_name.replace(' ', '_')
            fig = dict(data=data, layout=layout)
            py.offline.plot(fig, filename='gráficos/'+ aux_name2 +'.html')
            return fig
        except AttributeError:
            name = 'Hidrograma Série de Duração Parcial -  %s' % self.title
            layout = dict(
                title=name,
                showlegend=True,
                width=1890, height=827,
                xaxis=bandxaxis,
                yaxis=bandyaxis,
                font=dict(family='Time New Roman', size=34, color='rgb(0,0,0)'))

            data = []
            data.append(self._plot_one(self.data))
            data.append(self._plot_threshold())
            data += self._plot_event_peaks()

            aux_name = name.replace(' - ', '_')
            aux_name2 = aux_name.replace(' ', '_')
            fig = dict(data=data, layout=layout)
            py.offline.plot(fig, filename='gráficos/'+ aux_name2 +'.html')
            return fig

    def _plot_event_peaks(self):
        point_start = go.Scatter(x=self.peaks.Inicio,
                y=self.data.loc[self.peaks.Inicio],
                name = "Inicio do Evento",
                mode='markers',
                marker=dict(color='rgb(0, 0, 0)',
                            symbol = 'circle-dot',
                            size = 6),
                opacity = 1)

        point_end = go.Scatter(x=self.peaks.Fim,
            y=self.data.loc[self.peaks.Fim],
            name = "Fim do Evento",
            mode='markers',
            marker = dict(color = 'rgb(0, 0, 0)',
                          size = 6,
                          symbol = "x-dot"),
            opacity = 1)

        point_vazao = go.Scatter(x=self.peaks.index,
            y=self.data.loc[self.peaks.index],
            name = "Pico",
            mode='markers',
            marker=dict(size = 8,
                        color = 'rgb(128, 128, 128)',
                        line = dict(width = 1,
                                    color = 'rgb(0, 0, 0)'),),
            opacity = 1)

        return [point_start, point_end, point_vazao]

    def _plot_threshold(self):
        trace_threshold = go.Scatter(x=self.data.index,
            y=[self.threshold]*len(self.data),
            name = "Limiar",
            line =  dict(color = ('rgb(128, 128, 128)'),
                        width = 1.5,
                        dash = 'dot'))

        return trace_threshold

    def _plot_threshold_criterion(self, type_criterion):
        trace_threshold_criterion = go.Scatter(x=self.data.index,
                y=[self.threshold_criterion]*len(self.data),
                name = type_criterion.title(),
                line = dict(color = 'rgb(128, 128, 128)',
                            width = 1.5,
                            dash = 'dash'))
        return trace_threshold_criterion
