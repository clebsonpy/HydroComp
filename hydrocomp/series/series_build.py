import os
import pandas as pd
import plotly.figure_factory as FF

from abc import abstractmethod, ABCMeta

from hydrocomp.files import ana, ons
from hydrocomp.graphics.gantt import Gantt


class SeriesBuild(metaclass=ABCMeta):

    sources = {
        "ONS": ons.Ons,
        "ANA": ana.Ana
    }

    def __init__(self, data=None, path=os.getcwd(), source=None, *args, **kwargs):
        self.path = path
        if data is not None:
            try:
                self.station = kwargs['station']
                self.data = pd.DataFrame(data[self.station]).sort_index()
            except KeyError:
                self.station = None
                self.data = data
        else:
            try:
                self.station = kwargs['station']
            except KeyError:
                self.station = None
            if source in self.sources:
                self.source = source
                read = self.sources[self.source](self.path, *args, **kwargs)
                self.station = read.name
                self.data = read.data.sort_index()
            else:
                raise KeyError('Source not supported!')
        if self.data.size == 0:
            self.date_start, self.date_end = None, None
        else:
            self.date_start, self.date_end = self.__start_and_end()
            _data = pd.DataFrame(index=pd.date_range(start=self.date_start, end=self.date_end))
            self.data = _data.combine_first(self.data[self.date_start:self.date_end])

    @abstractmethod
    def month_start_year_hydrologic(self):
        pass

    @abstractmethod
    def plot_hydrogram(self, title, save=False, width=None, height=None, size_text=None):
        pass

    def __start_and_end(self):
        try:
            boolean = self.data.dropna(axis=0, how='all')
        except AttributeError:
            boolean = self.data
        date = boolean.index
        return date[0], date[-1]

    def __str__(self):
        """
        """
        return self.data.__repr__()

    def __getitem__(self, val):
        """
        """
        return self.__class__(data=self.data[val].copy())

    def date(self, date_start=None, date_end=None):
        """
        """
        if date_start is not None and date_end is not None:
            date_start = pd.to_datetime(date_start, dayfirst=True)
            date_end = pd.to_datetime(date_end, dayfirst=True)
            self.data = self.data.loc[date_start:date_end]
        elif date_start is not None:
            date_start = pd.to_datetime(date_start, dayfirst=True)
            self.data = self.data.loc[date_start:]
        elif date_end is not None:
            date_end = pd.to_datetime(date_end, dayfirst=True)
            self.data = self.data.loc[:date_end].copy()

    def less_period(self, data):
        """
        """
        aux = list()
        list_start = list()
        list_end = list()
        gantt_bool = data.isnull()
        for i in gantt_bool.index:
            if ~gantt_bool.loc[i]:
                aux.append(i)
            elif len(aux) > 2 and gantt_bool.loc[i]:
                list_start.append(aux[0])
                list_end.append(aux[-1])
                aux = []
        if len(aux) > 0:
            list_start.append(aux[0])
            list_end.append(aux[-1])
        dic = {'Start': list_start, 'Finish': list_end}
        return pd.DataFrame(dic)

    def summary(self):
        """
        """
        return self.data.describe()

    def get_year(self, year):
        """
        Seleciona todos os dados referente ao ano.
        """
        return self.__getitem__(year)

    def get_month(self, month):
        """
        Selecina todos os dados referente ao mês
        """
        return self.data.groupby(lambda x: x.month).get_group(month)

    def mean(self):
        """
        """
        return self.data.mean().values

    def std(self):
        """
        """
        return self.data.std()

    def quantile(self, percentile):
        return self.data.quantile(percentile).values

    def gantt(self, name):
        cont = 0
        df = pd.DataFrame(columns=['Task', 'Start', 'Finish', 'Description', 'IndexCol'])
        for i in self.data:
            df, cont = Gantt(self.data[i]).get_gantt(df, self.less_period(self.data[i]), cont)
        fig = FF.create_gantt(df, colors='#000000', group_tasks=True, title=name)
        return fig, df