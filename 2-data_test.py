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
#import plotly.express as px
import plotly.graph_objects as go
import datetime
import plotly
from plotly_resampler import FigureResampler


st.set_page_config(page_title="Testpage2", page_icon="📈")

st.title("testpage2")
st.write(
    "this is a test page 2."
)

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
st.write("Time of event:",gps)
st.write("Time of event:",from_gps(gps))
segment = ((gps)-16, (gps)+16)
st.write("Period of time with event in it:",segment)

time_center = gps



data = {}

ifos = ['L1', 'V1', 'H1']

for ifo in ifos:
    filename = f"GW190521_data/{ifo}_data_32s.hdf5"
    data[ifo] = TimeSeries.read(filename)


colours = {}
colours['H1'] = '#ee0000' # 'gwpy:ligo-hanford'
colours['L1'] = '#4ba6ff' # 'gwpy:ligo-livingston'
colours['V1'] = '#9b59b6' # 'gwpy:virgo'

labels ={}
labels['H1'] = 'LIGO-Hanford'
labels['L1'] = 'LIGO-Livingston'
labels['V1'] = 'Virgo'

st.write("Data type:       ",str(type(data['L1'])))
st.write("Data duration:   ",str(data['L1'].duration))
st.write("Data Sample Rate:",str(data['L1'].sample_rate))
st.write("Data delta t:    ",str(data['L1'].dt))
st.write("Data start time: ",str(data['L1'].x0))

#plot = GWPlot(figsize=(12, 4.8),dpi = 200)
#ax = plot.add_subplot(xscale='auto-gps')

#for ifo in ifos:
#   ax.plot(data[ifo],label=labels[ifo],color=colours[ifo])

#ax.set_epoch(time_center) # type: ignore

#ax.set_title('GW Strain data from our three Detectors')
#ax.set_ylabel('Strain noise')
#ax.legend(loc="best")

#st.pyplot(plot)

st.write("new plot test")

#st.write(data[ifo].times)
#st.write(data[ifo].times.value)
#st.write(time_center)
#st.write(data[ifo].times.value - time_center)

fig = go.Figure() #FigureResampler

#fig = FigureResampler(default_n_shown_samples=3_000)


for ifo in ifos:
    fig.add_trace(go.Scatter(
        x = data[ifo].times.value - time_center,
        y = data[ifo].value,
        mode='lines',
        line_color=colours[ifo],
        showlegend=True,
        name=labels[ifo],

    ))


fig.update_layout(
    title={
        'text':'GW Strain data from our {} Detectors'.format(str(len(ifos))),
        'y':0.9,
        'x':.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'automargin' : True},
    
    #xaxis_range=[data[ifo].xspan[0],data[ifo].xspan[1]]  )

    #xaxis = dict(
    #    tickmode = 'linear',
    #    tick0 = -32,
    #    dtick = 1
    #),
    #xaxis_range=[data[ifo].xspan[0],data[ifo].xspan[1]],
    

    xaxis=dict(
            title = "Time (s) relative to Time Center",
            rangeslider=dict(visible=False),
            type="linear"  #can do date too
        ),


    yaxis=dict(title="Strain"),
    margin=dict(l=60, r=20, t=60, b=60),

    #rangeslider_visible=True,
    #    rangeselector=dict(
    #        buttons=list([
                #dict(count=1, label="1m", step="month", stepmode="backward"),
                #dict(count=6, label="6m", step="month", stepmode="backward"),
                #dict(count=1, label="YTD", step="year", stepmode="todate"),
                #dict(count=1, label="1y", step="year", stepmode="backward"),
              #  dict(step="all")
    #        ])
    #    )

                )

#fig.show_dash(mode='inline')

st.plotly_chart(fig, theme="streamlit",on_select="rerun",use_container_width=True)
