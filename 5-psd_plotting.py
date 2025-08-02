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
from plotly_resampler import FigureResampler
from datetime import timedelta
from plotly_template import *
import time
from data_caching import *


st.set_page_config(page_title="FREQ PLOTS", page_icon="📈")

st.title("PSD plotting")
st.write(
    "this is a test page 3."
)

#del st.session_state["bandpass_data"]
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



def add_freq_event_marker(fig, marker_freq, line_color="green"):
    """
    Add a vertical event marker to a frequency plot.
    did have text too but that was taken out
    """
    fig.add_vline(
        x=marker_freq, 
        line_color=line_color,
        line_width=3,
    )


ASD_data = import_ASD_data()
ASD_fig = create_new_figure()
plot_freq_traces(ASD_fig,ASD_data,ifos=ifos)
apply_gw_freq_layout(ASD_fig,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19])

add_freq_event_marker(ASD_fig,80)
add_freq_event_marker(ASD_fig,30)

add_freq_event_marker(ASD_fig,25,"black")
add_freq_event_marker(ASD_fig,90,"black")

st.plotly_chart(ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)




PSD_data = import_PSD_data()
PSD_fig = create_new_figure()
plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")

add_freq_event_marker(PSD_fig,80)
add_freq_event_marker(PSD_fig,30)

add_freq_event_marker(PSD_fig,25,"black")
add_freq_event_marker(PSD_fig,90,"black")

st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)











PSD_data = import_PSD_data()
tukey_Pxx = import_tukey_PSD_data()
nowin_Pxx = import_nowindow_PSD_data()

tab1_window_fig = create_new_figure()
tab2_window_fig = create_new_figure()
tab3_window_fig = create_new_figure()


tab1, tab2, tab3 = st.tabs(["Livingston", "Hanford", "Virgo"])
with tab1:
    st.header("LIGO Livingston PSD comparison")
    ifo = "L1"
    plot_window_psd_trace(tab1_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab1_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab1_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')

    add_freq_event_marker(tab1_window_fig,80)
    add_freq_event_marker(tab1_window_fig,30)
    add_freq_event_marker(tab1_window_fig,25,"black")
    add_freq_event_marker(tab1_window_fig,90,"black")

    temp = nowin_Pxx[ifo]
    scale = (temp.value_at(168).value)*(168**2)
    tab1_window_fig.add_trace(go.Scatter(
        mode='lines',
        line_color="red",
        showlegend=True,
        name="1 / frequency<sup>2<sup>",
        opacity=.7
    ),

    hf_x = nowin_Pxx[ifo].frequencies[1:],
    hf_y = scale/nowin_Pxx[ifo].frequencies[1:]**2,
    limit_to_view=True,
    max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )

    apply_gw_freq_layout(tab1_window_fig,title = "LIGO Livingston PSD Windows", yrange = [-50,-38],xrange=[1.3,2.72],ytitle="? [HZ]")

    st.plotly_chart(tab1_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)



with tab2:
    st.header("LIGO Hanford PSD comparison")
    ifo = "H1"
    plot_window_psd_trace(tab2_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab2_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab2_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')

    add_freq_event_marker(tab2_window_fig,80)
    add_freq_event_marker(tab2_window_fig,30)
    add_freq_event_marker(tab2_window_fig,25,"black")
    add_freq_event_marker(tab2_window_fig,90,"black")


    temp = nowin_Pxx[ifo]
    scale = (temp.value_at(168).value)*(168**2)
    tab2_window_fig.add_trace(go.Scatter(
        mode='lines',
        line_color="red",
        showlegend=True,
        name="1 / frequency<sup>2<sup>",
        opacity=.7
    ),

    hf_x = nowin_Pxx[ifo].frequencies[1:],
    hf_y = scale/nowin_Pxx[ifo].frequencies[1:]**2,
    limit_to_view=True,
    max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )
    apply_gw_freq_layout(tab2_window_fig,title = "LIGO Hanford PSD Windows", yrange = [-50,-38],xrange=[1.3,2.72],ytitle="? [HZ]")

    st.plotly_chart(tab2_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)


with tab3:
    st.header("Virgo PSD comparison")
    ifo = "V1"
    plot_window_psd_trace(tab3_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab3_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab3_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')

    add_freq_event_marker(tab3_window_fig,80)
    add_freq_event_marker(tab3_window_fig,30)
    add_freq_event_marker(tab3_window_fig,25,"black")
    add_freq_event_marker(tab3_window_fig,90,"black")

    temp = nowin_Pxx[ifo]
    scale = (temp.value_at(168).value)*(168**2)
    tab3_window_fig.add_trace(go.Scatter(
        mode='lines',
        line_color="red",
        showlegend=True,
        name="1 / frequency<sup>2<sup>",
        opacity=.7
    ),

    hf_x = nowin_Pxx[ifo].frequencies[1:],
    hf_y = scale/nowin_Pxx[ifo].frequencies[1:]**2,
    limit_to_view=True,
    max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )
    apply_gw_freq_layout(tab3_window_fig,title = "LIGO Virgo PSD Windows", yrange = [-50,-38],xrange=[1.3,2.72],ytitle="? [HZ]")

    st.plotly_chart(tab3_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)

