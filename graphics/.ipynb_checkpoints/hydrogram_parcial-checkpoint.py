import plotly.graph_objs as go

from graphics.hydrogram_biuld import HydrogramBiuld


class HydrogramParcial(HydrogramBiuld):

    def __init__(self, data, peaks, threshold, title, threshold_criterion=None):
        super().__init__()
        self.data = data
        self.peaks = peaks
        self.threshold = threshold
        self.threshold_criterion = threshold_criterion
        self.title = title

    def plot(self, type_criterion=None):
        bandxaxis = go.XAxis(title="Data")
        bandyaxis = go.YAxis(title="Vazão(m³/s)")

        try:
            if self.threshold_criterion is None:
                raise AttributeError

            name = 'Hidrograma Série de Duração Parcial - %s' % self.title
            layout = dict(
                title=name,
                showlegend=True,
                width=1890, height=827,
                xaxis=bandxaxis, yaxis=bandyaxis,
                font=dict(family='Time New Roman', size=28, color='rgb(0,0,0)'))

            data = list()
            data += self._plot_one(self.data)
            data.append(self._plot_threshold())
            data.append(self._plot_threshold_criterion(type_criterion))
            data += self._plot_event_peaks()

            fig = dict(data=data, layout=layout)
            return data, fig

        except AttributeError:
            name = 'Hidrograma Série de Duração Parcial -  %s' % self.title
            layout = dict(
                title=name,
                showlegend=True,
                width=1890, height=827,
                xaxis=bandxaxis, yaxis=bandyaxis,
                font=dict(family='Time New Roman', size=28, color='rgb(0,0,0)'))

            data = list()
            data += self._plot_one(self.data)
            data.append(self._plot_threshold())
            data += self._plot_event_peaks()

            fig = dict(data=data, layout=layout)
            return data, fig

    def _plot_event_peaks(self):
        point_start = go.Scatter(
            x=self.peaks.Start, y=self.data.loc[self.peaks.Start],
            name="Inicio do Evento",
            mode='markers',
            marker=dict(color='rgb(0, 0, 0)',
                        symbol='circle-dot',
                        size=6),
            opacity=1)

        point_end = go.Scatter(
            x=self.peaks.End, y=self.data.loc[self.peaks.End],
            name="Fim do Evento",
            mode='markers',
            marker=dict(color='rgb(0, 0, 0)',
                        size=6,
                        symbol="x-dot"),
            opacity=1)

        point_vazao = go.Scatter(
            x=self.peaks.index,
            y=self.data.loc[self.peaks.index],
            name="Pico",
            mode='markers',
            marker=dict(size=8,
                        color='rgb(128, 128, 128)',
                        line=dict(width=1,
                                  color='rgb(0, 0, 0)'),),
            opacity=1)

        return [point_start, point_end, point_vazao]

    def _plot_threshold(self):
        trace_threshold = go.Scatter(
            x=self.data.index,
            y=[self.threshold]*len(self.data),
            name="Limiar",
            line=dict(color='rgb(128, 128, 128)',
                      width=1.5,
                      dash='dot')
        )

        return trace_threshold

    def _plot_threshold_criterion(self, type_criterion):
        trace_threshold_criterion = go.Scatter(
            x=self.data.index,
            y=[self.threshold_criterion]*len(self.data),
            #name=type_criterion.title(),
            name = "Mediana",
            line=dict(color='rgb(128, 128, 128)',
                      width=1.5,
                      dash='dash')
        )
        return trace_threshold_criterion