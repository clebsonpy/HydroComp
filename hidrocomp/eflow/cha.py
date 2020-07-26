import pandas as pd
import plotly.graph_objs as go
from hidrocomp.statistic.normal import Normal
from hidrocomp.statistic.bootstrap import Bootstrap
from hidrocomp.eflow.exceptions import *
from hidrocomp.eflow.graphics import GraphicsCha


class Cha:

    def __init__(self):
        self._point = None
        self._aspects: dict = {}
        self._classification = None

    @property
    def aspects(self):
        return self._aspects

    @aspects.setter
    def aspects(self, aspect):
        self._aspects[aspect.name] = aspect

    @property
    def point(self):
        if self._point is None:
            df = pd.DataFrame()
            for i in self.aspects:
                df = df.combine_first(self.aspects[i].point)
            self._point = df
        return self._point

    @staticmethod
    def __definition_classification(points) -> str:
        if points == 0:
            return "{} Points - Un-impacted".format(points)
        elif 1 <= points <= 4:
            return "{} Points - Low risk of impact".format(points)
        elif 5 <= points <= 10:
            return "{} Points - Moderate risk of impact".format(points)
        elif 11 <= points <= 20:
            return "{} Points - High risk of impact".format(points)
        elif 21 <= points <= 30:
            return "{} Points - Severely impacted".format(points)

    @property
    def classification(self):
        points = self.point.sum().sum()
        if self._classification is None:
            self._classification = self.__definition_classification(points=points)
        return self._classification

    def plot(self, data_type="diff"):
        data_type_dict = {'std': "Standard deviation", "mean": "Mean"}
        data = []
        symbol = {'Magnitude': 'circle', 'Magnitude and Duration': 'x', 'Timing Extreme': 'cross',
                  'Frequency and Duration': 'triangle-up', 'Rate and Frequency': 'diamond'}
        x = []
        error = []
        error_minus = []
        for i in self.aspects:
            graphs = GraphicsCha(obj_dhram=self.aspects[i], data_type=data_type, xaxis="Variable",
                                 yaxis="Abnormality")
            fig, df = graphs.plot(type="error_bar")

            data_fig = fig["data"]
            error = error + list(df["Data"].values + df["Error"].values)
            error_minus = error_minus + list(df["Data"].values - df["Error_minus"].values)
            x = x + list(df["Variable"].values)
            data_fig[0]["name"] = i
            data_fig[0]["marker"]["color"] = "black"
            data_fig[0]["marker"]["symbol"] = symbol[i]
            data = data + [data_fig[0]]
        layout = fig["layout"]
        layout["title"]["text"] = f"Difference - {data_type_dict[data_type]}"

        fig = go.Figure(data=data, layout=layout)
        fig.add_trace(go.Scatter(
            x=x, y=[4]*len(x),
            mode='lines',
            line=dict(width=0.5, color='#2EFE2E'),
            stackgroup="one",
            showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=x, y=[2] * len(x),
            mode='lines',
            line=dict(width=0.5, color='#F7FE2E'),
            stackgroup="one",
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=x, y=[2] * len(x),
            mode='lines',
            line=dict(width=0.5, color='#FAAC58'),
            stackgroup="one",
            showlegend=False
        ))
        if max(error) > 8:
            fig.add_trace(go.Scatter(
                x=x, y=[max(error)-8] * len(x),
                mode='lines',
                line=dict(width=0.5, color='#FE2E2E'),
                stackgroup="one",
                showlegend=False
            ))
        fig.add_trace(go.Scatter(
            x=x, y=[-4] * len(x),
            mode='lines',
            line=dict(width=0.5, color='#2EFE2E'),
            stackgroup="two",
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=x, y=[-2] * len(x),
            mode='lines',
            line=dict(width=0.5, color='#F7FE2E'),
            stackgroup="two",
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=x, y=[-2] * len(x),
            mode='lines',
            line=dict(width=0.5, color='#FAAC58'),
            stackgroup="two",
            showlegend=False
        ))
        if min(error_minus) < -8:
            fig.add_trace(go.Scatter(
                x=x, y=[min(error_minus)+8] * len(x),
                mode='lines',
                line=dict(width=0.5, color='#FE2E2E'),
                stackgroup="two",
                showlegend=False
            ))
        return fig, data


class ChaAspect:

    def __init__(self, name):
        self.name = name
        self._abnormality = None
        self._variables: dict = {}
        self._list_name_variables = []

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, variable):
        self._list_name_variables.append(variable.name)
        self._variables[variable.name] = variable

    @property
    def values_mean(self):
        df = pd.DataFrame()
        for i in self.variables:
            df = df.combine_first(self.variables[i].value_mean)
        return df.reindex(self._list_name_variables)

    @property
    def values_std(self):
        df = pd.DataFrame()
        for i in self.variables:
            df = df.combine_first(self.variables[i].value_std)
        return df.reindex(self._list_name_variables)

    @property
    def abnormality(self):
        if self._abnormality is None:
            df = pd.DataFrame()
            for i in self.variables:
                df = df.combine_first(self.variables[i].abnormality)
            self._abnormality = df.reindex(self._list_name_variables)
        return self._abnormality

    @property
    def point(self):
        diff_mean = self.abnormality.abs().mean()
        df = pd.DataFrame(columns=["Mean", "Std"])
        df.at[self.name, "Mean"] = self.__definition_points(diff_mean["Abnormality_mean"])
        df.at[self.name, "Std"] = self.__definition_points(diff_mean["Abnormality_std"])
        return df

    @staticmethod
    def __definition_points(multi_pre):
        if 1 < multi_pre <= 2:
            return 1
        elif 2 < multi_pre <= 3:
            return 2
        elif multi_pre > 3:
            return 3
        else:
            return 0

    def plot(self, data_type="mean"):
        graphs = GraphicsCha(obj_dhram=self, data_type=data_type, xaxis="Variable", yaxis="Abnormality")
        fig, data = graphs.plot(type="error_bar")
        return fig, data


class ChaVariable:

    def __init__(self, variable_pre, variable_pos, interval: int, m: int):
        self.name = variable_pre.name
        self.data_pre = variable_pre.data
        self.data_pos = variable_pos.data
        self.interval = [((100 - interval) / 2) / 100, 1 - ((100 - interval) / 2) / 100]
        self.sample_pre = Bootstrap(data=self.data_pre, m=m, name=self.name)
        self.sample_pos = Bootstrap(data=self.data_pos, m=m, name=self.name)

    def __calc_value(self, dist_pre, dist_pos):
        value = pd.DataFrame(columns=["Pre - 2_5", "Pre - 97_5", "Pos - 2_5", "Pos - 97_5", "Pre - mean", "Pos - mean"])
        confidence_intervals_pre = dist_pre.data.quantile(self.interval)
        confidence_intervals_pos = dist_pos.data.quantile(self.interval)
        zscore_pre_2_5 = dist_pre.z_score(confidence_intervals_pre[self.interval[0]])
        zscore_pos_2_5 = dist_pre.z_score(confidence_intervals_pos[self.interval[0]])
        zscore_pre_97_5 = dist_pre.z_score(confidence_intervals_pre[self.interval[1]])
        zscore_pos_97_5 = dist_pre.z_score(confidence_intervals_pos[self.interval[1]])
        zscore_pre_mean = dist_pre.z_score(dist_pre.data.mean())
        zscore_pos_mean = dist_pre.z_score(dist_pos.data.mean())

        value.at[self.name, "Pre - 2_5"] = zscore_pre_2_5
        value.at[self.name, "Pre - mean"] = zscore_pre_mean
        value.at[self.name, "Pre - 97_5"] = zscore_pre_97_5

        value.at[self.name, "Pos - 2_5"] = zscore_pos_2_5
        value.at[self.name, "Pos - mean"] = zscore_pos_mean
        value.at[self.name, "Pos - 97_5"] = zscore_pos_97_5
        return value

    @property
    def value_mean(self):

        dist_pre = Normal(data=self.sample_pre.mean())
        dist_pos = Normal(data=self.sample_pos.mean())

        value = self.__calc_value(dist_pre=dist_pre, dist_pos=dist_pos)
        return value

    @property
    def value_std(self):

        dist_pre = Normal(data=self.sample_pre.std())
        dist_pos = Normal(data=self.sample_pos.std())

        value = self.__calc_value(dist_pre=dist_pre, dist_pos=dist_pos)

        return value

    @staticmethod
    def __calc_abnormality(pos_2_5, pos_97_5):
        if abs(pos_2_5) < abs(pos_97_5):
            value_pos = pos_2_5
        else:
            value_pos = pos_97_5

        multi_diff = (abs(abs(value_pos) - 2) / 2) * value_pos/abs(value_pos)
        return multi_diff

    @property
    def abnormality(self) -> pd.DataFrame:

        diff_df = pd.DataFrame(columns=["Abnormality_mean", "Abnormality_std"])

        z_score_mean = self.value_mean
        z_score_std = self.value_std
        pos_mean_2_5, pos_std_2_5 = z_score_mean["Pos - 2_5"].values[0], z_score_std["Pos - 2_5"].values[0]
        pos_mean_97_5, pos_std_97_5 = z_score_mean["Pos - 97_5"].values[0], z_score_std["Pos - 97_5"].values[0]

        value_mean_pos = self.__calc_abnormality(pos_mean_2_5, pos_mean_97_5)
        value_std_pos = self.__calc_abnormality(pos_std_2_5, pos_std_97_5)

        diff_df.at[self.name, "Abnormality_mean"] = value_mean_pos
        diff_df.at[self.name, "Abnormality_std"] = value_std_pos

        return diff_df

    def plot(self, color={"pre": "blue", "pos": "red"}, type="mean"):
        """
        @type color: dict
        """
        if type == "mean":
            fig_obs, data_obs = GraphicsCha(obj_dhram=self, color=color, name=self.name).plot(type="point")
            fig_nat, data_nat = GraphicsCha(obj_dhram=self, color=color, name=self.name).plot(type="point")
        elif type == "std":
            fig_obs, data_obs = GraphicsCha(obj_dhram=self, color=color, name=self.name).plot(type="point")
            fig_nat, data_nat = GraphicsCha(obj_dhram=self, color=color, name=self.name).plot(type="point")
        else:
            raise AttributeError("Type Error")

        data = data_obs + data_nat
        fig = dict(data=data, layout=fig_nat['layout'])

        return fig, data

    def __str__(self):
        return self.name