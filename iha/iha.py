from iha.exceptions import NotStation
import pandas as pd
import calendar as cal
from series.flow import Flow


class IHA:

    def __init__(self, data, month_water=None, station=None):
        self.flow = Flow(data)
        self.station = self.get_station(station)
        self.month_start = self.get_month_start(month_water)

    def rva(self):
        pass

    def mean(self):
        pass

    def std(self):
        pass

    def get_station(self, station):
        if len(self.flow.data.columns.values) != 1:
            if station is None:
                raise NotStation("Station requirement")
            else:
                if station in self.flow.data.columns.values:
                    return station
                else:
                    raise NotStation("Not station")
        else:
            get_station = self.flow.data.columns.values[0]
            self.flow.data = pd.DataFrame(self.flow.data[get_station])

            return get_station

    def get_month_start(self, month_water):
        if month_water is None:
            return self.flow.month_start_year_hydrologic(station=self.station)
        else:
            return cal.month_abbr[month_water].upper()

    # Group 1: Magnitude of monthly water conditions
    def magnitude(self):
        years = self.flow.data.groupby(pd.Grouper(freq='A'))
        data = pd.DataFrame()
        for year in years:
            aux = year[1].groupby(pd.Grouper(freq='M')).mean()
            df = pd.DataFrame({year[0].year: {
                cal.month_name[i.month]: aux[self.station][i] for i in aux[self.station].index}})
            data = data.combine_first(df)
        mean_months = data.T

        mean = pd.DataFrame(mean_months.mean(), columns=['Means'])
        std = pd.DataFrame(mean_months.std() / mean_months.mean(), columns=['Coeff. of Var.'])
        iha_mean_month = mean.combine_first(std)
        return iha_mean_month

    # Group 2: Magnitude and Duration of annual extreme water conditions
    def magnitude_and_duration(self):
        aver_data = pd.DataFrame()
        for i in [1, 3, 7, 30, 90]:
            ave_max = self.flow.data.rolling(window=i).mean().groupby(pd.Grouper(freq='A')).max()
            ave_min = self.flow.data.rolling(window=i).mean().groupby(pd.Grouper(freq='A')).min()
            years = ave_max.index.year
            df1 = pd.DataFrame(pd.Series(data=ave_min[self.station].values, name='%s-day minimum' % i, index=years))
            df2 = pd.DataFrame(pd.Series(data=ave_max[self.station].values, name='%s-day maximum' % i, index=years))
            aver_data = aver_data.combine_first(df1)
            aver_data = aver_data.combine_first(df2)
            if i == 7:
                mean_year = self.flow.data[self.station].groupby(pd.Grouper(freq='A')).mean().values
                base_flow = pd.DataFrame(pd.Series(data=ave_min[self.station].values / mean_year,
                                                   name='Base flow index', index=years))
                aver_data = aver_data.combine_first(base_flow)

        dic_zero = {i[0].year: i[1].loc[i[1][self.station].values == 0].sum()
                    for i in self.flow.data.groupby(pd.Grouper(freq='A'))}

        aver_data = aver_data.combine_first(pd.DataFrame(pd.Series(data=dic_zero, name='Number of zero days')))

        mean = pd.DataFrame(aver_data.mean(), columns=['Means'])
        cv = pd.DataFrame(aver_data.std() / aver_data.mean(), columns=['Coeff. of Var.'])

        iha_moving_aver = mean.combine_first(cv)
        return iha_moving_aver

    # Group 3: Timing of annual extreme water conditions
    def timing_extreme(self):

        day_julian_max = pd.DatetimeIndex(self.flow.data[self.station].groupby(pd.Grouper(freq='A')).idxmax().values)
        day_julian_min = pd.DatetimeIndex(self.flow.data[self.station].groupby(pd.Grouper(freq='A')).idxmin().values)

        df_day_julian_max = pd.DataFrame(list(map(int, day_julian_max.strftime("%j"))), index=day_julian_max.year,
                                         columns=["Date of maximum"])
        df_day_julian_min = pd.DataFrame(list(map(int, day_julian_min.strftime("%j"))), index=day_julian_min.year,
                                         columns=["Date of minimum"])

        # combine the dfs of days julians
        df_day_julian = df_day_julian_max.combine_first(df_day_julian_min)

        mean = pd.DataFrame(df_day_julian.mean(), columns=['Means'])
        cv = pd.DataFrame(df_day_julian.std() / df_day_julian.mean(), columns=['Coeff. of Var.'])
        iha_day_julian = mean.combine_first(cv)

        return iha_day_julian

    # Group 4: Frequency and duration of high and low pulses
    def frequency_and_duration(self, station, type_threshold, type_event, type_criterion, value_threshold, **kwargs):
        events = self.flow.parcial(station=self.station, type_threshold=type_threshold, type_criterion=type_criterion,
                                   type_event=type_event, value_threshold=value_threshold)

        duration_pulse_high = pd.DataFrame(events.peaks.groupby(pd.Grouper(freq='A')).Duration.mean()).rename(
            columns={"Duration": 'High pulse duration'})
        print(duration_pulse_high)
        """
        # eventosPicos, limiar = self.parcialPorAno(2.3, tipoEvento)
        eventosPicos = self.eventos_picos(eventosL, tipoEvento)

        # print(self.test_autocorrelacao(eventosPicos)[0])

        grupoEventos = self.dataFlow[self.nPosto].groupby(pd.Grouper(freq='A'))
        dic = {'Ano': [], 'Duracao': [], 'nPulsos': []}
        for i, serie in grupoEventos:
            dic['Ano'].append(i.year)
            dic['Duracao'].append(eventosPicos.Duracao.loc[eventosPicos.Ano == i.year].mean())
            dic['nPulsos'].append(len(eventosPicos.loc[eventosPicos.Ano == i.year]))
        evento_por_ano = pd.DataFrame(dic)
        evento_por_ano.set_value(evento_por_ano.loc[evento_por_ano.Duracao.isnull()].index, 'Duracao', 0)
        durMedia = evento_por_ano.Duracao.mean()
        durCv = evento_por_ano.Duracao.std() / durMedia
        nPulsoMedio = evento_por_ano.nPulsos.mean()
        nPulsoCv = evento_por_ano.nPulsos.std() / nPulsoMedio
        return eventosPicos, evento_por_ano, durMedia, durCv, nPulsoMedio, nPulsoCv, limiar
        """

    # Group 5: Rate and frequency of water condition changes
    def rate_and_frequency(self):
        pass
