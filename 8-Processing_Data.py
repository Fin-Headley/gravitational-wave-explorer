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



st.set_page_config(page_title="Processing Data", page_icon="📈",layout="wide")

st.title("Your turn!")
st.write(
    "Try and find the GW190521 event by applying a bandpass and whitening the data!"
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


datetime_center = Time(time_center, format='gps').utc.datetime

ifos = ['L1', 'V1','H1']

for ifo in ifos:
    bandpass_data[ifo] = bandpass_data[ifo].crop(gps-2,gps+2)
    whitend_data[ifo]  = whitend_data[ifo].crop(gps-2,gps+2)



colors = load_colours_dict()


##########################################################################################################################
if 'whiten_left_plot' not in st.session_state:
    st.session_state.whiten_left_plot = False
if 'bandpass_right_plot' not in st.session_state:
    st.session_state.bandpass_right_plot = False
if 'bandpass_hint' not in st.session_state:
    st.session_state.bandpass_hint = False



# Create a button to toggle the line visibility
if st.checkbox(":blue[Hint]"):
    st.session_state.bandpass_hint = True
else:
    st.session_state.bandpass_hint = False


if st.session_state.bandpass_hint == True:
    st.write(""":blue-background[Toggle whitening on and drag the upper frequency slider down until you can see a strong triple peak in Livingston and Handford.]
             
:blue-background[Then bring the lower frequency up until Livingston keeps similar shape when you toggle whitening on/off.]
""")

low_bandpass, high_bandpass = st.slider("Select your bandpass frequency bounds:", .01, 500.0, (.01, 500.0))

slider_bandpass = {}
slider_whiten = {}

for ifo in ifos:
    slider_bandpass[ifo] = pure_data[ifo].bandpass(low_bandpass, high_bandpass)
    slider_whiten[ifo] = slider_bandpass[ifo].whiten(asd=np.sqrt(PSD_data[ifo]))

    slider_bandpass[ifo] = slider_bandpass[ifo].crop(gps-.2,gps+.2)
    slider_whiten[ifo] = slider_whiten[ifo].crop(gps-.2,gps+.2)




button_col1, button_col2 = st.columns(2)

with button_col1:
    # Create a button to toggle the line visibility
    if st.checkbox("Whiten the Strain timeseries"):
        st.session_state.whiten_left_plot = True
        y_timeseries_title = "Normalized Strain "
        timeseries_title = "Whitened Strain Data With Given Bandpass"


    else:
        st.session_state.whiten_left_plot = False
        y_timeseries_title  = "Strain"
        timeseries_title = "Strain Data With Given Bandpass"
with button_col2:
    # Create a button to toggle the line visibility
    if st.checkbox("Show selected Bandpass with shading"):
        st.session_state.bandpass_right_plot = True
    else:
        st.session_state.bandpass_right_plot = False
    pass



plotting_timeseries = {}
if st.session_state.whiten_left_plot == True:
    plotting_timeseries = slider_whiten
elif st.session_state.whiten_left_plot == False:
    plotting_timeseries = slider_bandpass


graph_col1, graph_col2, graph_col3 = st.columns([10,1,10],gap=None)

with graph_col1:
    
    tab1, tab2, tab3 = st.tabs(["Single Detector","Two Detectors","Three Detectors"])

    with tab1:
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.0,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)

        multiplot1_apply_gw_strain_layout(fig_resampler,timeseries_title=timeseries_title,y_timeseries_title=y_timeseries_title)

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)

    with tab2:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.03,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)
        
        add_GW_trace_subplot(fig_resampler,plotting_timeseries["H1"].times.value,plotting_timeseries["H1"].value,colors["H1"],"Hanford",row=2,col=1)

        multiplot2_apply_gw_strain_layout(fig_resampler,timeseries_title=timeseries_title,y_timeseries_title=y_timeseries_title,legend_loc =(.98,.45))

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)

    with tab3:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["H1"].times.value,plotting_timeseries["H1"].value,colors["H1"],"Hanford",row=2,col=1)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["V1"].value,colors["V1"],"Virgo",row=3,col=1)

        multiplot3_apply_gw_strain_layout(fig_resampler,timeseries_title=timeseries_title,y_timeseries_title=y_timeseries_title,legend_loc =(.01,.3))

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)




ASD_slider_bandpass = create_new_figure()
ASD_data = load_ASD_data()

plot_freq_traces(ASD_slider_bandpass,ASD_data,ifos=ifos)

ASD_slider_bandpass.update_layout( #change to fig.update_layout and put in function
        # Hover settings
        hovermode='x unified',
        autosize=False,
        width=600,
        height=500,

        # Y-axis settings
        yaxis=dict(
            #title="Power Spectral Density(PSD)",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            type="log",
            range =  [-24,-20],
            #linewidth=1, 
            #linecolor='black', 
            #mirror=True, 
            #showline=True,
        ),
        
        # X-axis settings
        xaxis=dict(
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            #showgrid=True,
            hoverformat=".3",#"Time: %H:%M:%S.%3f",
            range =[1.2,2.7],
            #linewidth=1, linecolor='black',mirror=True, showline=True
        ),

        # Legend settings
            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=.9,
                        xanchor="right",
                        x=1
                    ),
            #bordercolor = "black",
            #borderwidth =1

    )

apply_gw_freq_layout_no_buttons(ASD_slider_bandpass,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19.9],xrange=[1,2.7],ytitle="Strain/√Hz")


if st.session_state.bandpass_right_plot == True:
    add_freq_event_shading(ASD_slider_bandpass, high_bandpass, 2000., "red",opacity=.1)
    add_freq_event_shading(ASD_slider_bandpass, 0, low_bandpass, "red",opacity=.1)

with graph_col3:
    st.tabs([" "])

    st.plotly_chart(ASD_slider_bandpass, theme="streamlit",on_select="rerun",use_container_width=False)

with graph_col2:
    st.tabs(" ")

##########################################################################################################################


