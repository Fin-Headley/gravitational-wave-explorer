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
from matched_filtering_functions import *

st.set_page_config(page_title="Model Playground", page_icon="📈",layout="wide")

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
datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

ifos = ['L1', 'V1','H1']
########################################################################
col1, col2 = st.columns(2)

with col1:

    st.title("Model Testing Ground")
    st.write(
        'Using the same parameters from the example model, try and find model parameters that line up with the GW190521 data!')

    minicol1, minicol2 = st.columns(2)

    with minicol1:
        mass = st.slider("The mass of the higher mass object (Solar Masses):",
                        min_value=20.0
                        ,max_value=300.0
                        ,value=135.0    #,value=160.0
                        ,key="mass_slider"
                        )

        mass_ratio = st.slider("The ratio of mass between the binary objects:",
                        min_value=0.01
                        ,max_value=1.0
                        ,value=.54      #,value=.72
                        ,key="ratio_slider"
                        )

        
        right_ascension = st.slider("Right Ascension (Radians):",
                        min_value=0.0          
                        ,max_value= 2* np.pi
                        ,value=2.0      #,value=2.2
                        ,key="ra_slider"
                        )

        phase = st.slider("Coalesence phase of the binary (radians):",
                        min_value=0.0            
                        ,max_value= 2* np.pi
                        ,value=.72      #,value=.01
                        ,key="phase_slider"
                        )


    event_time = st.slider("The detected time of the GW event:",
                            min_value = datetime_center-timedelta(seconds=.1)
                            ,max_value=datetime_center+timedelta(seconds=.1)
                            ,value=datetime_center+timedelta(seconds=-.057)      #,value=datetime_center+timedelta(seconds=.027)
                            ,step=timedelta(seconds=.001)
                            ,format = "h:mm:ss.SSS"
                            ,key="T_S_slider"
                            )
with minicol2:
        distance = st.slider("The Luminosity distance to the GW event (Mega-Parsecs):",
                            min_value=100.0
                            ,max_value=5000.0
                            ,value=1600.0           #,value=2400.0
                            ,key="distance_slider"
                            )



        inclination = st.slider("Inclination angle (radians):",
                        min_value=0.0
                        ,max_value= np.pi
                        ,value=.82           #,value=.5
                        ,key="incl_slider"
                        )

        declination = st.slider("Declination (Radians):",
                                min_value= -np.pi/2 
                                ,max_value= np.pi/2
                                ,value= -.95        #,value= -1.2
                                ,key="dec_slider"
                                )
        

        polarization = st.slider("Strain Polarization (radians):",
                min_value=0.0 
                ,max_value= 2*np.pi
                ,value=1.01      #,value=.01
                ,key="pol_slider"
                )






time_shift = float((event_time - datetime_center).total_seconds())
user_params = [mass, mass_ratio, distance, time_shift, phase, right_ascension, declination, inclination, polarization]


param0=[160,.72,2400,.027,0.1, 2.2, -1.2, 0.5, 0.01] 
#m1, q, distance, time_shift, phase, right_ascension, declination, inclination, polarization = param

#template0 = gen_template(param0)


user_model = gen_template(user_params)

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
fig_resampler = FigureResampler(fig)

########################################################################


L1_white_template = user_model["L1"].whiten(asd=np.sqrt(PSD_data["L1"]),highpass=25.,lowpass = 90.)
H1_white_template = user_model["H1"].whiten(asd=np.sqrt(PSD_data["H1"]),highpass=25.,lowpass = 90.)
V1_white_template = user_model["V1"].whiten(asd=np.sqrt(PSD_data["V1"]),highpass=25.,lowpass = 90.)


colors = load_colours_dict()

########################################################################


with col2:



    tab1, tab2, tab3 = st.tabs(["Single Detector","Two Detectors","Three Detectors"])


    with tab1:
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
        add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)

        apply_gw_1_model_comparision_layout(fig_resampler,title='CBC Model vs Data')
        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
        st.caption("Your whitened GW model compared to whitened and bandpassed Ligo-Livingston strain data.",help=graph_help_no_buttons())


    with tab2:

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
        add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)

        add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
        add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford Model",row=2,col=1)

        apply_gw_2_model_comparision_layout(fig_resampler,title='CBC Model vs Data')

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
        st.caption("Your whitened GW model compared to whitened and bandpassed Ligo strain data.",help=graph_help_no_buttons())



    with tab3:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
        fig_resampler = FigureResampler(fig)

        add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
        add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
        add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["V1"].value,colors["V1"],"Virgo",row=3,col=1)

        add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)
        add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford Model",row=2,col=1)
        add_GW_trace_subplot(fig_resampler,V1_white_template.times.value,V1_white_template.value,"black","Virgo Model",row=3,col=1)

        apply_gw_3_model_comparision_layout(fig_resampler,title='CBC Model vs Data')

        st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
        st.caption("Your whitened GW model compared to whitened and bandpassed Ligo/Virgo strain data.",help=graph_help_no_buttons())

st.divider()


st.write("If you are struggling to find a good set of parameters, feel free to take a look at my initial guess!")

if 'model_playground_hint' not in st.session_state:
    st.session_state.model_playground_hint = False

Good_parameter_values = {"Mass":160, "Ratio":.72,"Right Ascension":2.2,
                         "Coalesence Phase":.01,"Luminosity Distance":2400,
                         "Inclination":.5,"Declination":-1.2,"Polarization":.01,
                         "Time of the event":"3:02:29:427"}

if st.checkbox(":blue[Show my starting parameters]",key="model_playground_hint_checkbox"):
    st.session_state.model_playground_hint = True
else:
    st.session_state.model_playground_hint = False


if st.session_state.model_playground_hint == True:        
    st.table(Good_parameter_values)

