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
from plotly_resampler import FigureResampler # type: ignore

st.set_page_config(page_title="Testpage2", page_icon="📈",layout="wide")

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
st.write("Data start time: ",str(Time(data['L1'].x0, format='gps').utc.datetime)) # pyright: ignore[reportAttributeAccessIssue]

st.write("new plot test")

#st.write(data[ifo].times)
#st.write(data[ifo].times.value)
#st.write(time_center)

#st.write(data[ifo].times.value - time_center)

#fig = go.Figure() #FigureResampler



stacked = st.radio(
    "Plot Strain side by side or stack plots on each other",
    ["Offset", "Stacked"],
    #captions=[],
    index=0,
    horizontal= True
)

if stacked == "Offset":
    offset = dict(L1 = 0, H1 = +1.2e-18, V1 = -1.2e-18)
    st.write("Each detector can be turned on and off by clicking the legend.")
else:
    st.write("Each detector can be turned on and off by clicking the legend.")
    offset = dict(L1 = 0, H1 = 0, V1 = 0)

fig = FigureResampler()

for ifo in ifos:

    times = data[ifo].times.value          # array of GPS seconds
    t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime            # pyright: ignore[reportAttributeAccessIssue] # pyright: ignore[reportAttributeAccessIssue] # numpy array of Python datetimes in UTC     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0
                                    #lets do things in numbers and put calculate date in after
    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=colours[ifo],
        showlegend=True,
        name=labels[ifo],
    ),
    hf_x = x_datetime,
    hf_y = data[ifo].value+offset[ifo],
    limit_to_view=True,
    max_n_samples = 30000
    )

fig.add_vline(Time(time_center, format='gps').utc.datetime) # pyright: ignore[reportAttributeAccessIssue]

fig.update_layout(

    updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.1, y=1.15, xanchor="center", yanchor="bottom",
            buttons=[
                dict(label="±0.1 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [Time(time_center+-.1, format='gps').utc.datetime,  # pyright: ignore[reportAttributeAccessIssue]
                                                                     Time(time_center+.1, format='gps').utc.datetime]}]), # type: ignore
                dict(label="±0.2 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [Time(time_center-.2, format='gps').utc.datetime,  # type: ignore
                                                                     Time(time_center+.2, format='gps').utc.datetime]}]), # type: ignore
                dict(label="±.5 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [Time(time_center-.5, format='gps').utc.datetime,  # type: ignore
                                                                     Time(time_center+.5, format='gps').utc.datetime]}]), # type: ignore
                dict(label="±1 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [Time(time_center-1, format='gps').utc.datetime,  # type: ignore
                                                                     Time(time_center+1, format='gps').utc.datetime]}]), # type: ignore
                dict(label="All (±16 s)", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [Time(time_center-16, format='gps').utc.datetime,  # type: ignore
                                                                     Time(time_center+16, format='gps').utc.datetime]}]), # type: ignore
            ]
        )],


    title={
        'text':'Observed GW Strain Data',
        'y':0.9,
        'x':.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'automargin' : True},
    

    yaxis=dict(title="Strain"),

    #xaxis=dict(
    #        title = "Time (s) relative to Time Center",
    #        rangeslider=dict(visible=False),
    #        type="linear",  #can do date too
    #        ),


    xaxis=go.layout.XAxis(
        rangeslider=dict(visible=True),
        title = "Time (seconds) since "+str(Time(data["L1"].t0, format='gps').utc.datetime).format("fits"), # type: ignore
        type="date",
        #range = [Time(time_center-3, format='gps').utc.datetime, Time(time_center+3, format='gps').utc.datetime]
        tickformat="%S.%f",
    )
)


st.plotly_chart(fig, theme="streamlit",on_select="rerun",use_container_width=True)
