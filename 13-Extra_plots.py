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

datetime_center = Time(time_center, format='gps').utc.datetime

colors = load_colours_dict()


##########################################################################################################################
st.header("moving bandpass")

if 'whiten_left_plot' not in st.session_state:
    st.session_state.whiten_left_plot = False
if 'bandpass_right_plot' not in st.session_state:
    st.session_state.bandpass_right_plot = False
if 'bandpass_hint' not in st.session_state:
    st.session_state.bandpass_hint = False


# Create a button to toggle the line visibility
if st.checkbox("Hint"):
    st.session_state.bandpass_hint = True
else:
    st.session_state.bandpass_hint = False


if st.session_state.bandpass_hint == True:
    st.write("The Bandpass I went with was ",25.,",",90.,"Try starting there!")

low_bandpass, high_bandpass = st.slider("Select a range of values", .02, 500.0, (25.0, 90.0))
st.write("Values:", low_bandpass, high_bandpass)

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
    if st.checkbox("Toggle whiten Visability time series plot"):
        st.session_state.whiten_left_plot = True
    else:
        st.session_state.whiten_left_plot = False
with button_col2:
    # Create a button to toggle the line visibility
    if st.checkbox("Toggle Bandpass Shading"):
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
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)

        fig_resampler.update_layout(
            #width=700,
            height=500,
            hovermode='x unified',

            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=.9,
                        xanchor="right",
                        x=1
                    )
            
        )
        st.write("")

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)

    with tab2:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["H1"].times.value,plotting_timeseries["H1"].value,colors["H1"],"Hanford",row=2,col=1)

        fig_resampler.update_layout(
            #width=700,
            height=500,
            hovermode='x unified',
            
            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=.45,
                        xanchor="right",
                        x=1
                    )
            
        )

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)

    with tab3:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["L1"].value,colors["L1"],"Livingston",row=1,col=1)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["H1"].times.value,plotting_timeseries["H1"].value,colors["H1"],"Hanford",row=2,col=1)

        add_GW_trace_subplot(fig_resampler,plotting_timeseries["L1"].times.value,plotting_timeseries["V1"].value,colors["V1"],"Virgo",row=3,col=1)

        fig_resampler.update_layout(
            #width=700,
            height=500,
            hovermode='x unified',
            
            legend=dict(
                        orientation="v",
                        yanchor="bottom",
                        y=.6,
                        xanchor="right",
                        x=1
                    )
            
        )


        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)





PSD_slider_bandpass = create_new_figure()


PSD_slider_data = {}

PSD_data = load_PSD_data()

plot_freq_traces(PSD_slider_bandpass,PSD_data,ifos=ifos)

PSD_slider_bandpass.update_layout( #change to fig.update_layout and put in function
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
            range =  [-47.3,-42],
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

#apply_gw_freq_layout(PSD_slider_bandpass,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle="? [HZ]")


if st.session_state.bandpass_right_plot == True:
    add_freq_event_shading(PSD_slider_bandpass, high_bandpass, 2000., "red",opacity=.1)
    add_freq_event_shading(PSD_slider_bandpass, 0, low_bandpass, "red",opacity=.1)

with graph_col3:
    st.tabs([" "])

    st.plotly_chart(PSD_slider_bandpass, theme="streamlit",on_select="rerun",use_container_width=False)

with graph_col2:
    st.tabs(" ")

##########################################################################################################################

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


apply_gw_fourier_layout(Fourier_phase_fig_tab1,title = "Livingston Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase")
apply_gw_fourier_layout(Fourier_phase_fig_tab2,title = "Hanford Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase")
apply_gw_fourier_layout(Fourier_phase_fig_tab3,title = "Virgo Raw Data FFT",yrange = [-np.pi,np.pi],xrange=[15,400],ytitle="Phase")


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




# raw data
Pure_fig = create_new_figure()
plot_traces(Pure_fig,pure_data,ifos)
#add_event_marker(fig=Pure_fig, marker_time = datetime_center, marker_name=" Rough Time of Event", line_color="green")
apply_gw_strain_layout(Pure_fig,title='Pure Observed GW Strain Data')
st.plotly_chart(Pure_fig, theme="streamlit",on_select="rerun",use_container_width=True)



raw_fig = create_new_figure()
plot_traces(raw_fig,raw_data,ifos)
#add_event_marker(fig=raw_fig, marker_time = datetime_center, marker_name="", line_color="green")
apply_gw_strain_layout(raw_fig,title='Cropped Raw Observed GW Strain Data',data_range="raw")
st.plotly_chart(raw_fig, theme="streamlit",on_select="rerun",use_container_width=True)


ifos = ['H1','V1','L1']

bp_fig = create_new_figure()
plot_traces(bp_fig,bandpass_data,ifos)
#add_event_marker(fig=bp_fig, marker_time = datetime_center, marker_name="", line_color="green")
apply_gw_strain_layout(bp_fig,title='Bandpassed Observed GW Strain Data',data_range="bandpass")
st.plotly_chart(bp_fig, theme="streamlit",on_select="rerun",use_container_width=True)


ifos = ['H1','V1','L1']
white_fig = create_new_figure()
plot_traces(white_fig,whitend_data,ifos)
#add_event_marker(fig=white_fig, marker_time = datetime_center, marker_name="", line_color="green")
apply_gw_strain_layout(white_fig,title='Whitened GW Strain Data',data_range="whiten")
st.plotly_chart(white_fig, theme="streamlit",on_select="rerun",use_container_width=True)


ifos = ['L1', 'H1','V1']
GW_fig = create_new_figure()
plot_traces(GW_fig,GW_data,ifos)
#add_event_marker(fig=GW_fig, marker_time = datetime_center, marker_name="", line_color="green")
apply_gw_strain_layout(GW_fig,title='Whiten and Bandpassed GW Strain Data',data_range="GW_data")
st.plotly_chart(GW_fig, theme="streamlit",on_select="rerun",use_container_width=True)




