import streamlit as st
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from gwosc.datasets import find_datasets
from gwosc.datasets import event_gps
from gwpy.time import to_gps
from gwpy.time import from_gps
from pycbc.waveform import get_td_waveform
from scipy.signal import gausspulse
from scipy.optimize import minimize
from IPython.display import display, clear_output
from pycbc.detector import Detector
from gwpy.timeseries import TimeSeries
from scipy.signal import get_window
from astropy import units as u
from gwpy.plot import Plot as GWPlot
import os
from astropy.time import Time
import plotly.express as px
import plotly.graph_objects as go
import datetime
import plotly
from plotly_resampler import FigureResampler # type: ignore
from datetime import timedelta
from plotly_template import *
import time
from data_caching import *
from matched_filtering_functions import *
import arviz as az
import pandas as pd

st.set_page_config(page_title="Q_transform", page_icon="📈",layout="wide")

st.title("Results:")
st.write(
    "lets take a look at my best fitting paramters!"
)

pure_data = load_pure_data()
raw_data = load_raw_data()
bandpass_data = load_bandpass_data()
whitend_data = load_whitend_data()
GW_data = load_GW_data()


PSD_data = load_PSD_data()

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps
datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

ifos = ['L1','H1','V1']
########################################################################

MAP_df = pd.read_parquet("MAP_parameters.parquet")
MAP_df.rename(inplace=True,index={"TimeShift":"Time Shift","RA":"Right Ascension","Dec":"Declination","Incl":"Inclination","Pol":"Polarization","lp":"Log Posterior","chain":"Chain","draw":"Draw"})

#results_df = MAP_df.copy()
column_dec_value = {"Mass":1,"Ratio":2,"Distance":0,"Time Shift":5,"Phase":2,"Right Ascension":4,"Declination":3,"Inclination":2,"Polarization":3}
column_titles = np.array(["Mass","Ratio","Distance","Time Shift","Phase","Right Ascension","Declination","Inclination","Polarization"])

MAP_params = []
for i in range(9):
    MAP_params.append(MAP_df["MAP"].iloc[i])

best_fit_template = gen_template(MAP_params)
data = load_raw_data()

data_qspecgram = {}

subtracted_qspecgram = {}


for ifo in ifos:
    subtracted = data[ifo] - best_fit_template[ifo]

    data_qspecgram[ifo]=data[ifo].whiten(asd=np.sqrt(PSD_data[ifo])).q_transform(outseg=(time_center - .5, time_center + .5),frange=(15, 150))
    subtracted_qspecgram[ifo]=subtracted.whiten(asd=np.sqrt(PSD_data[ifo])).q_transform(outseg=(time_center - .5, time_center + .5),frange=(15, 150))

#st.write((data_qspecgram['L1']))

data_times = load_raw_data()
data_times["L1"].crop(gps-.5,gps+.5)
times = data_times["L1"].times.value
t = Time(times, format='gps')         
x_datetime = t.utc.datetime    # type: ignore


def add_qtransform_subplot(fig,qspecgram,ifo='L1',name="hello",showscale = False,colorbar=dict(title = "colorbar"),row=1,col=1):
    data_times = load_raw_data()
    data_times["L1"].crop(gps-.5,gps+.5)
    times = data_times["L1"].times.value
    t = Time(times, format='gps')        
    x_datetime = t.utc.datetime    # type: ignore

    zvar=0
    if ifo=='L1':
        zvar=150
    elif ifo=='H1':
        zvar=90
    elif ifo=='V1':
        zvar=60

    fig.add_trace(go.Heatmap(
        x = x_datetime,
        y0 = 15,
        dy=(150-15)/len((qspecgram[ifo][0])),
        z = qspecgram[ifo].T,
        zmin = 0,
        zmax = zvar,
        colorscale=px.colors.sequential.Viridis,    #Purples,gray_r
        colorbar=colorbar,
        showscale = showscale,
        #zmin = 0,
        #customdata = coordinate_array,
        hovertemplate='<b>Time</b>: %{x}</br><b>Frequency</b>: %{y} Hz<br><b>Count</b>: %{z}<extra></extra>',
        #yaxis='y',
        #xaxis='x',
        ),
        row=row,
        col=col,
    )

#Q_fig=go.Figure()

#fig.add_trace(heatmap)

#st.plotly_chart(fig,use_container_width=False)

Q_fig = make_subplots(rows=3, cols=2, shared_xaxes="all", horizontal_spacing=.03 ,vertical_spacing=0.05,shared_yaxes="all")# type: ignore #column_titles=[labels["L1"]+" SNR",labels["H1"]+" SNR",labels["V1"]+" SNR"])

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='L1',name="hello",row=1,col=1,showscale=True,colorbar=dict(title="Livingston", len=0.33, y=0.70,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='L1',name="hello",row=1,col=2)

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='H1',name="hello",row=2,col=1,showscale=True,colorbar=dict(title="Hanford", len=0.33, y=0.35,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='H1',name="hello",row=2,col=2)

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='V1',name="hello",row=3,col=1,showscale=True,colorbar=dict(title="Virgo", len=0.33, y=0,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='V1',name="hello",row=3,col=2)

Q_fig.update_layout(
    #hovermode='closest',
    #bargap=0.05,
    width=800,
    height=900,

    title={
        'text': "Q transform check",
        'y': .98,
        'x': .5,
        'xanchor': 'center',
        'yanchor': 'top',
        #'automargin': True
    },

    xaxis=dict(
    title="Strain Spectrogram",
    side='top',

    ),

    xaxis2=dict(
    title="Model Subtracted Spectrogram",
    side='top',

    ),

    xaxis3=dict(

    ),

    xaxis4=dict(

    ),

    xaxis5=dict(
    type="date",
    showgrid=True,

    ),

    xaxis6=dict(
    type="date",
    showgrid=True,
    ),

)

st.plotly_chart(Q_fig,use_container_width=False)
