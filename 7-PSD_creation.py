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




st.set_page_config(page_title="PSD Creation", page_icon="📈")

st.title("How is the PSD made")
st.write(
    "Lets look at what the PSD is and some important steps in making it!"
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




st.header("Show or hide Bandpass filter")

tab1, tab2 = st.tabs(["Without Bandpass Shading", "With Bandpass Shading"])

with tab1:

    PSD_data = import_PSD_data()
    PSD_fig = create_new_figure()

    plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
    apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")

    st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)


with tab2:

    PSD_data = import_PSD_data()
    PSD_fig = create_new_figure()

    add_freq_event_shading(PSD_fig, 30, 80, "chartreuse")
    add_freq_event_shading(PSD_fig, 25, 30, "yellow")
    add_freq_event_shading(PSD_fig, 80, 90, "yellow")
    add_freq_event_marker(PSD_fig,25,"black")
    add_freq_event_marker(PSD_fig,90,"black")

    plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
    apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")

    st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)
