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

pure_data = import_pure_data()
raw_data = import_raw_data()
bandpass_data = create_bandpass_data()
whitend_data = create_whitend_data()
GW_data = import_GW_data()

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps
ifos = ['V1', 'H1','L1']

datetime_center = Time(time_center, format='gps').utc.datetime



# raw data

raw_fig = create_new_figure()
plot_traces(raw_fig,raw_data,ifos)
add_event_marker(fig=raw_fig, marker_time = datetime_center, marker_name=" Time of Event", line_color="green")
apply_gw_strain_layout(raw_fig,title='Raw Observed GW Strain Data')
st.plotly_chart(raw_fig, theme="streamlit",on_select="rerun",use_container_width=True)



# ASD plot

ASD_data = import_ASD_data()
ASD_fig = create_new_figure()
plot_freq_traces(ASD_fig,ASD_data,ifos=ifos)
apply_gw_freq_layout(ASD_fig,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19])

#add_freq_event_marker(ASD_fig,80,"green")
#add_freq_event_marker(ASD_fig,30,"green")
#add_freq_event_marker(ASD_fig,25,"black")
#add_freq_event_marker(ASD_fig,90,"black")

ASD_fig.add_vrect(x0=30, x1=80,
              annotation_text="Signal!", annotation_position="top left",
              annotation=dict(font_size=20, font_family="Times New Roman"),
              fillcolor="green", opacity=0.25, line_width=0)

st.plotly_chart(ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)


