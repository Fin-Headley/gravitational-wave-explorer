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




st.set_page_config(page_title="PSD Creation", page_icon="📈",layout="wide")

st.title("Removing Noise")
st.write(
    "Lets take a closer look at the steps needed to remove unwanted noise from GW data."
)

st.divider()

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
ifos = ['V1', 'H1','L1']

datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

colors = load_colours_dict()


st.header("hello")

if 'show_bandpass' not in st.session_state:
    st.session_state.show_bandpass = False

# Create a button to toggle the line visibility
if st.checkbox("Toggle Bandpass Visability this graph"):
    st.session_state.show_bandpass = True
else:
    st.session_state.show_bandpass = False

#plot the data

PSD_data = load_PSD_data()
PSD_fig = create_new_figure()

plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")


if st.session_state.show_bandpass:
    add_freq_event_shading(PSD_fig, 30, 80, "chartreuse")
    add_freq_event_shading(PSD_fig, 25, 30, "yellow")
    add_freq_event_shading(PSD_fig, 80, 90, "yellow")
    add_freq_event_marker(PSD_fig,25,"black")
    add_freq_event_marker(PSD_fig,90,"black")

st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)

if st.session_state.show_bandpass:
    st.write("showing bandpass filter")
else:
    st.write("hiding bandpass filter")




###########################################################################################################################################################################







PSD_data = load_PSD_data()
tukey_Pxx = load_tukey_PSD_data()
nowin_Pxx = load_nowindow_PSD_data()

tab1_window_fig = create_new_figure()
tab2_window_fig = create_new_figure()
tab3_window_fig = create_new_figure()

if 'show_bandpass_tab1' not in st.session_state:
    st.session_state.show_bandpass_tab1 = False

if 'show_bandpass_tab2' not in st.session_state:
    st.session_state.show_bandpass_tab2 = False

if 'show_bandpass_tab3' not in st.session_state:
    st.session_state.show_bandpass_tab3 = False

##########################################################################################################################
tab1, tab2, tab3 = st.tabs(["Livingston", "Hanford", "Virgo"])
with tab1:
    st.header("LIGO Livingston PSD comparison")

    # Create a button to toggle the bandpass visibility
    if st.checkbox("Toggle Livingston Bandpass Visability"):
        st.session_state.show_bandpass_tab1 = True
    else:
        st.session_state.show_bandpass_tab1 = False

    ifo = "L1"
    plot_window_psd_trace(tab1_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab1_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab1_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')


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


    if st.session_state.show_bandpass_tab1:
        add_freq_event_shading(tab1_window_fig, 30, 80, "chartreuse")
        add_freq_event_shading(tab1_window_fig, 25, 30, "yellow")
        add_freq_event_shading(tab1_window_fig, 80, 90, "yellow")
        add_freq_event_marker(tab1_window_fig,25,"black")
        add_freq_event_marker(tab1_window_fig,90,"black")

    st.plotly_chart(tab1_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)

##########################################################################################################################
with tab2:
    st.header("LIGO Hanford PSD comparison")

    # Create a button to toggle the bandpass visibility
    if st.checkbox("Toggle Hanford Bandpass Visability"):
        st.session_state.show_bandpass_tab2 = True
    else:
        st.session_state.show_bandpass_tab2 = False



    ifo = "H1"
    plot_window_psd_trace(tab2_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab2_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab2_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')


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

    if st.session_state.show_bandpass_tab2:
        add_freq_event_shading(tab2_window_fig, 30, 80, "chartreuse")
        add_freq_event_shading(tab2_window_fig, 25, 30, "yellow")
        add_freq_event_shading(tab2_window_fig, 80, 90, "yellow")
        add_freq_event_marker(tab2_window_fig,25,"black")
        add_freq_event_marker(tab2_window_fig,90,"black")


    st.plotly_chart(tab2_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)

with tab3:
    st.header("Virgo PSD comparison")

    # Create a button to toggle the bandpass visibility
    if st.checkbox("Toggle Virgo Bandpass Visability"):
        st.session_state.show_bandpass_tab3 = True
    else:
        st.session_state.show_bandpass_tab3 = False


    ifo = "V1"
    plot_window_psd_trace(tab3_window_fig,nowin_Pxx,ifo =ifo,color="purple",name="No Window")
    plot_window_psd_trace(tab3_window_fig,tukey_Pxx,ifo =ifo,color="green",name="Tukey Window")
    plot_window_psd_trace(tab3_window_fig,PSD_data,ifo =ifo,color="black",name='Welch Average')

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

    if st.session_state.show_bandpass_tab3:
        add_freq_event_shading(tab3_window_fig, 30, 80, "chartreuse")
        add_freq_event_shading(tab3_window_fig, 25, 30, "yellow")
        add_freq_event_shading(tab3_window_fig, 80, 90, "yellow")
        add_freq_event_marker(tab3_window_fig,25,"black")
        add_freq_event_marker(tab3_window_fig,90,"black")

    st.plotly_chart(tab3_window_fig, theme="streamlit",on_select="rerun",use_container_width=True)



##########################################################################################################################
st.header("Fourier phases")


Fourier_phase_fig_tab1 = create_new_figure()
Fourier_phase_fig_tab2 = create_new_figure()
Fourier_phase_fig_tab3 = create_new_figure()

plot_both_fourier_freq_traces(Fourier_phase_fig_tab1,"L1")
plot_both_fourier_freq_traces(Fourier_phase_fig_tab2,"H1")
plot_both_fourier_freq_traces(Fourier_phase_fig_tab3,"V1")


apply_gw_fourier_layout(Fourier_phase_fig_tab1,title = "Livingston Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase") # type: ignore
apply_gw_fourier_layout(Fourier_phase_fig_tab2,title = "Hanford Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase") # type: ignore
apply_gw_fourier_layout(Fourier_phase_fig_tab3,title = "Virgo Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase") # type: ignore


tab1, tab2, tab3 = st.tabs(["Livingston", "Hanford", "Virgo"])
with tab1:
    st.header("LIGO Livingston Fourier Phase Graph")
    st.plotly_chart(Fourier_phase_fig_tab1, theme="streamlit",on_select="rerun",use_container_width=True)

with tab2:
    st.header("LIGO Hanford Fourier Phase Graph")
    st.plotly_chart(Fourier_phase_fig_tab2, theme="streamlit",on_select="rerun",use_container_width=True)


with tab3:
    st.header("Virgo Fourier Phase Graph")
    st.plotly_chart(Fourier_phase_fig_tab3, theme="streamlit",on_select="rerun",use_container_width=True)


