#!/usr/bin/env python
# coding: utf-8

# # BC 776 - Lebrija

# In[1]:


DEVICE_NAME = 'BC 776 - Lebrija'
PICKLED_DATA_FILENAME = 'data_monthly.pkl'
project_path = 'D:\OneDrive - CELSIA S.A E.S.P\Proyectos\Eficiencia_Energetica\Bancolombia\Experimental'
import warnings
warnings.filterwarnings("ignore")


# In[2]:


import pandas as pd
import numpy as np
import datetime as dt
import json

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px

pio.renderers.default = "notebook"
pio.templates.default = "plotly_white"


# Import bespoke modules
import sys
from pathlib import Path

project_path = Path(project_path)
sys.path.append(str(project_path))

import config as cfg
from library_ubidots import Ubidots

from library_report_v2 import Cleaning as cln
from library_report_v2 import Graphing as grp
from library_report_v2 import Processing as pro
from library_report_v2 import Configuration as repcfg


# ## Functions

# In[3]:


def show_response_contents(df):
    print("The response contains:")
    print(json.dumps(list(df['variable'].unique()), sort_keys=True, indent=4))
    print(json.dumps(list(df['device'].unique()), sort_keys=True, indent=4))


# ## Preprocessing

# In[4]:


data_path = project_path / 'data'
df = pd.read_pickle(data_path / PICKLED_DATA_FILENAME)
df = df.query("device_name == @DEVICE_NAME")
show_response_contents(df)


# In[5]:


df = df.sort_values(by=['variable','datetime'])
df = pro.datetime_attributes(df)

df_bl, df_st = pro.split_into_baseline_and_study(df, baseline=cfg.BASELINE, study=cfg.STUDY, inclusive='both')

# df_cons = df.query("variable == 'front-consumo-activa'")
# df_ea = cln.recover_energy_from_consumption(df_cons, new_varname='front-energia-activa-acumulada')
# df_pa_synth = cln.differentiate_single_variable(df_ea, 'front-potencia-activa-sintetica', remove_gap_data=True)
# df_ea_interp = cln.linearly_interpolate_series(df_ea, data_rate_in_minutes=None)


# In[6]:


df_pa = df.query("variable == 'front-potencia-activa'").copy()
cargas = df_st[df_st["variable"].isin(cfg.ENERGY_VAR_LABELS)].copy()
front = df_st[df_st["variable"].isin(['front-consumo-activa'])].copy()
front_reactiva = df_st[df_st["variable"].isin(['consumo-energia-reactiva-total'])].copy()

df_pa = cln.remove_outliers_by_zscore(df_pa, zscore=4)
cargas = cln.remove_outliers_by_zscore(cargas, zscore=4)
front = cln.remove_outliers_by_zscore(front, zscore=4)
front_reactiva = cln.remove_outliers_by_zscore(front, zscore=4)


# In[7]:


cargas_hour = cargas.groupby(by=["variable"]).resample('1h').sum().round(2).reset_index().set_index('datetime')
cargas_hour = pro.datetime_attributes(cargas_hour)

cargas_day = cargas.groupby(by=["variable"]).resample('1D').sum().reset_index().set_index('datetime')
cargas_day = pro.datetime_attributes(cargas_day)

cargas_month = cargas.groupby(by=["variable"]).resample('1M').sum().reset_index().set_index('datetime')
cargas_month = pro.datetime_attributes(cargas_month)

front_hour = front.groupby(by=["variable"]).resample('1h').sum().round(2).reset_index().set_index('datetime')
front_hour = pro.datetime_attributes(front_hour)

front_day = front.groupby(by=["variable"]).resample('1D').sum().reset_index().set_index('datetime')
front_day = pro.datetime_attributes(front_day)

front_month = front.groupby(by=["variable"]).resample('1M').sum().reset_index().set_index('datetime')
front_month = pro.datetime_attributes(front_month)

front_reactiva_hour = front_reactiva.groupby(by=["variable"]).resample('1h').sum().round(2).reset_index().set_index('datetime')
front_reactiva_hour = pro.datetime_attributes(front_reactiva_hour)


# ## Resultados

# In[8]:


front_cons_total = front_month.iloc[-1]["value"]
# dif_mes_anterior =front_month.iloc[-1]["value"] - past_months.iloc[-1]["value"]
print(f"El consumo de energía durante el último mes fue {front_cons_total:.1f}kWh")


# In[9]:


cargas_cons_total = cargas_month['value'].sum()
consumo_otros =  front_cons_total - cargas_cons_total

if (consumo_otros < 0):
    consumo_otros = 0

df_pie = cargas_month[['variable','value']].copy()

df_pie.loc[-1] = ['otros', consumo_otros]
df_pie = df_pie.reset_index(drop=True)
df_pie['value'] = df_pie['value'].round(1)


if (df_pie.value >= 0).all():
    fig = px.pie(
        df_pie, 
        values="value", 
        names='variable', 
        hover_data=['value'], 
        labels={'variable':'Carga', 'value':'Consumo [kWh]'},
        title="Consumo total de energía activa por carga [kWh]",
        color_discrete_sequence=repcfg.FULL_PALETTE, 
    )

    fig.update_layout(
        font_family=repcfg.CELSIA_FONT,
        font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
        font_color=repcfg.FULL_PALETTE[1],
        title_x=repcfg.PLOTLY_TITLE_X,
        width=repcfg.JBOOK_PLOTLY_WIDTH,
        height=repcfg.JBOOK_PLOTLY_HEIGHT
    )

    fig.update_traces(
        textposition='inside', 
        textinfo='percent', 
        insidetextorientation='radial'
    )

    fig.update(
        layout_showlegend=True
    )

    fig.show()


# In[10]:


fig = px.bar(
    front_day.reset_index(),
    x="day",
    y="value",
    labels={'day':'Día', 'value':'Consumo [kWh]'},
    title="Frontera: Consumo diario de energía activa [kWh] en el último mes",
)

fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)

fig.update_traces(marker_color=grp.hex_to_rgb(repcfg.FULL_PALETTE[0]))
fig.show()


# In[11]:


fig = px.bar(
    pd.concat([cargas_day, front_day]),
    x="day",
    y="value",
    barmode='group',
    color='variable',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Consumo [kWh]'},
    title="Consumo diario de energía activa [kWh] en el último mes",
)

fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)

fig.show()


# In[12]:


df_pa_bl, df_pa_st = pro.split_into_baseline_and_study(df_pa, baseline=cfg.BASELINE, study=cfg.STUDY, inclusive='both')

if (len(df_pa_bl) > 0) & (len(df_pa_st) > 0):
    df_pa_bl_day = (
        df_pa_bl
        .reset_index()
        .groupby(['device_name','variable','hour'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    df_pa_st_day = (
        df_pa_st
        .reset_index()
        .groupby(['device_name','variable','hour'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    grp.compare_baseline_day_by_hour(
        df_pa_bl_day,
        df_pa_st_day,
        title=f"Día típico para la sede de {DEVICE_NAME}",
        bl_label="Promedio línea base",
        st_label="Promedio octubre",
        bl_ci_label="Intervalo línea base",
        include_ci=True,
        fill_ci=True
    )


    df_pa_bl_week = (
        df_pa_bl
        .reset_index()
        .groupby(['device_name','variable','cont_dow'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    df_pa_st_week = (
        df_pa_st
        .reset_index()
        .groupby(['device_name','variable','cont_dow'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    grp.compare_baseline_week_by_day(
        df_pa_bl_week,
        df_pa_st_week,
        title=f"Semana típica para la sede de {DEVICE_NAME}",
        bl_label="Promedio línea base",
        st_label="Promedio octubre",
        bl_ci_label="Intervalo línea base",
        include_ci=True,
        fill_ci=True
    )


# In[13]:


matrix = front_hour.pivot(index='day', columns='hour', values='value')

if (matrix.shape[0] > 0) & (matrix.shape[1] > 0):
    data = grp.pivoted_dataframe_to_plotly_heatmap(matrix)
    grp.hourly_heatmap(
        data,
        title="Frontera: Consumo total de energía activa [kWh] en el último mes"
    )


# In[14]:


matrix = (
    cargas_hour
    .groupby(by=["day","hour"]).sum().reset_index()
    .pivot(index='day', columns='hour', values='value')
)

if (matrix.shape[0] > 0) & (matrix.shape[1] > 0):
    data = grp.pivoted_dataframe_to_plotly_heatmap(matrix)
    grp.hourly_heatmap(
        data,
        title="Cargas: Consumo total de energía activa [kWh] en el último mes"
    )


# In[15]:


matrix = (
    front_reactiva_hour
    .groupby(by=["day","hour"]).sum().reset_index()
    .pivot(index='day', columns='hour', values='value')
)

if (matrix.shape[0] > 0) & (matrix.shape[1] > 0):
    data = grp.pivoted_dataframe_to_plotly_heatmap(matrix)
    grp.hourly_heatmap(
        data,
        title="Cargas: Consumo total de energía reactiva [kVArh] en el último mes"
    )


# In[16]:


df_plot = pd.concat([front_hour, cargas_hour])

list_vars = [
    'front-consumo-activa',
    'aa-consumo-activa',
    'ilu-consumo-activa'
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    df_var = df_plot.query("variable == @variable")
    hex_color = repcfg.FULL_PALETTE[idx % len(repcfg.FULL_PALETTE)]
    rgba_color = grp.hex_to_rgb(hex_color, alpha)
    idx += 1

    if (len(df_var) > 0):
        fig.add_trace(go.Scatter(
            x=df_var.index,
            y=df_var.value,
            line_color=rgba_color,
            name=variable,
            showlegend=True,
        ))



fig.update_layout(
    title="Consumo de energía activa [kWh]",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Consumo Activa [kWh]")
)

fig.update_traces(mode='lines')
# fig.update_xaxes(rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# In[17]:


cargas_nighttime_cons = cargas[cargas["hour"].isin(cfg.NIGHT_HOURS)].copy()
cargas_nighttime_cons = pro.datetime_attributes(cargas_nighttime_cons)

cargas_daily_nighttime_cons = (
    cargas_nighttime_cons
    .groupby('day')['value']
    .sum()
    .to_frame()
)

if (cargas_daily_nighttime_cons.shape[0] > 0):
    fig = px.bar(
        cargas_daily_nighttime_cons.reset_index(),
        x="day",
        y="value",
        labels={'day':'Día', 'value':'Consumo [kWh]'},
        title="Cargas: Consumo nocturno de energía activa [kWh] en el último mes",
    )

    fig.update_layout(
        font_family=repcfg.CELSIA_FONT,
        font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
        font_color=repcfg.FULL_PALETTE[1],
        title_x=repcfg.PLOTLY_TITLE_X,
        width=repcfg.JBOOK_PLOTLY_WIDTH,
        height=repcfg.JBOOK_PLOTLY_HEIGHT
    )

    fig.update_traces(marker_color=grp.hex_to_rgb(repcfg.FULL_PALETTE[0]))
    fig.show()

    consumo_nocturno = round(cargas_daily_nighttime_cons["value"].sum(),2)

    print(f"Durante el mes pasado se consumió un total de: {consumo_nocturno}kWh fuera del horario establecido")

