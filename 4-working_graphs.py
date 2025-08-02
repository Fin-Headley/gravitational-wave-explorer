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
from plotly_template import *
import time
from data_caching import *

st.set_page_config(page_title="graphing_development", page_icon="📈",layout="wide")

st.title("graphing development")
st.write(
    "this is a page to work on some graphing issues."
)

#del st.session_state["bandpass_data"]
pure_data = import_pure_data()
raw_data = import_raw_data()
bandpass_data = import_bandpass_data()
whitend_data = import_whitend_data()
GW_data = import_GW_data()


#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps

ifos = ['L1', 'V1', 'H1']

st.write("Data type:       ",str(type(GW_data['L1'])))
st.write("Data duration:   ",str(GW_data['L1'].duration))
st.write("Data Sample Rate:",str(GW_data['L1'].sample_rate))
st.write("Data delta t:    ",str(GW_data['L1'].dt))
st.write("Data start time: ",str(GW_data['L1'].x0))
st.write("Data start time: ",str(Time(GW_data['L1'].x0, format='gps').utc.datetime))

datetime_center = Time(time_center, format='gps').utc.datetime

st.write("Event time: ",datetime_center)

#st.write("TimeDelta Test: ",datetime_center+ timedelta(seconds = 2))

st.write(datetime_center.strftime('%a %d %b %Y, %I:%M:%S.%f')[:-3]+datetime_center.strftime(' %p'))



raw_fig = create_new_figure()
plot_traces(raw_fig,raw_data,ifos)
add_event_marker(fig=raw_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(raw_fig,title='Raw Observed GW Strain Data')
st.plotly_chart(raw_fig, theme="streamlit",on_select="rerun",use_container_width=True)


#st.write(fig.data[0]["x"][0].strftime('%M:%S.%f'))

#st.write(len(fig.data[0]["x"]))


bp_fig = create_new_figure()
plot_traces(bp_fig,bandpass_data,ifos)
add_event_marker(fig=bp_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(bp_fig,title='Bandpassed Observed GW Strain Data')
st.plotly_chart(bp_fig, theme="streamlit",on_select="rerun",use_container_width=True)


white_fig = create_new_figure()
plot_traces(white_fig,whitend_data,ifos)
add_event_marker(fig=white_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(white_fig,title='Whitened GW Strain Data')
st.plotly_chart(white_fig, theme="streamlit",on_select="rerun",use_container_width=True)


GW_fig = create_new_figure()
plot_traces(GW_fig,GW_data,ifos)
add_event_marker(fig=GW_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(GW_fig,title='Whiten and Bandpassed GW Strain Data')
st.plotly_chart(GW_fig, theme="streamlit",on_select="rerun",use_container_width=True)

