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
#import plotly.express as px
import plotly.graph_objects as go
import datetime
import plotly
from plotly_resampler import FigureResampler # type: ignore
from datetime import timedelta
from plotly_template import *
import time
from data_caching import *


st.set_page_config(page_title="Exploring GW Data", page_icon="📈")

st.title("Exploring GW Data")
st.write(
    "Lets import and explore some Gravitational Wave Data!"
)

pure_data = load_pure_data()
raw_data = load_raw_data()
bandpass_data = load_bandpass_data()
whitend_data = load_whitend_data()
GW_data = load_GW_data()

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps
ifos = ['V1', 'H1','L1']

datetime_center = Time(time_center, format='gps').utc.datetime

st.write(st.session_state)


# raw data

raw_fig = create_new_figure()
plot_traces(raw_fig,raw_data,ifos)
add_event_marker(fig=raw_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(raw_fig,title='Raw Observed GW Strain Data')
st.plotly_chart(raw_fig, theme="streamlit",on_select="rerun",use_container_width=True)



# PSD plot

PSD_data = load_PSD_data()
PSD_fig = create_new_figure()

plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")

st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)
