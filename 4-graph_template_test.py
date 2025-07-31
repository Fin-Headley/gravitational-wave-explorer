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
from datetime import timedelta
import plotly.io as pio

import my_template

st.set_page_config(page_title="template_testing", page_icon="📈",layout="wide")

st.title("graphing development")
st.write(
    "this is a page to work on some graphing issues."
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

short_labels ={}
short_labels['H1'] = 'Hanford'
short_labels['L1'] = 'Livingston'
short_labels['V1'] = 'Virgo'


st.write("Data type:       ",str(type(data['L1'])))
st.write("Data duration:   ",str(data['L1'].duration))
st.write("Data Sample Rate:",str(data['L1'].sample_rate))
st.write("Data delta t:    ",str(data['L1'].dt))
st.write("Data start time: ",str(data['L1'].x0))
st.write("Data start time: ",str(Time(data['L1'].x0, format='gps').utc.datetime))

datetime_center = Time(time_center, format='gps').utc.datetime

st.write("Event time: ",datetime_center)

#st.write("TimeDelta Test: ",datetime_center+ timedelta(seconds = 2))

st.write(datetime_center.strftime('%a %d %b %Y, %I:%M:%S.%f')[:-3]+datetime_center.strftime(' %p'))


theme_text_color = st.get_option('theme.textColor')
theme_primary_color = st.get_option('theme.primaryColor')
theme_bc_color = st.get_option('theme.backgroundColor')
theme_bc_2_color = st.get_option('theme.secondaryBackgroundColor')
theme_sidebar_primary_color = st.get_option('theme.sidebar.secondaryBackgroundColor')
theme_sidebar_bg_color = st.get_option('theme.sidebar.backgroundColor')
theme_WidgetBorder_color = st.get_option('theme.showWidgetBorder')


fig = FigureResampler(resampled_trace_prefix_suffix = ("",""), default_n_shown_samples = 1000, show_mean_aggregation_size= False, create_overview=True)

for ifo in ifos:

    times = data[ifo].times.value          # array of GPS seconds
    t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime            # numpy array of Python datetimes     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0
                                    #lets do things in numbers and put calculate date in after
    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=colours[ifo],
        showlegend=True,
        name=short_labels[ifo],
        template="my_custom_template",
    ),
    hf_x = x_datetime,
    hf_y = data[ifo].value,
    limit_to_view=True,
    max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )

t0 =x_datetime[0]

fig.add_vrect(x0 = datetime_center, 
                x1 = datetime_center+timedelta(microseconds=1), 
                line_color="green",
                line_width=4,
                 annotation= dict(
                    text=" Time of Event",
                    font=dict( #family="Courier New, monospace",
                        size=12,
                        color=theme_text_color,),
                    bgcolor=theme_bc_color,
                    opacity=1,
                    y=.85,
                    xanchor="left", 
                    yanchor="bottom",
                    showarrow=False,
                    ),
                annotation_position = "outside top right",)


fig.update_layout(template="my_custom_template")

st.plotly_chart(fig, theme="streamlit",on_select="rerun",use_container_width=True)

