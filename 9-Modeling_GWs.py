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

st.set_page_config(page_title="Modeling Gravitational Waves", page_icon="📈",layout="wide")

st.title("Modeling Gravitational Waves")
st.write(
    "Lets look at how we can model GWs!"
)

pure_data = import_pure_data()
raw_data = import_raw_data()
bandpass_data = create_bandpass_data()
whitend_data = create_whitend_data()
GW_data = import_GW_data()


PSD_data = import_PSD_data()

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps
datetime_center = Time(time_center, format='gps').utc.datetime

ifos = ['L1', 'V1','H1']
########################################################################
col1, col2, col3, col4,col5 = st.columns(5)


with col1:

    mass = st.slider("The mass of the higher mass object (Solar Masses):",
                    min_value=50.0
                    ,max_value=300.0
                    ,value=160.0
                    )

    right_ascension = st.slider("Right Ascension (Radians):",
                    min_value=0.0          
                    ,max_value= 2* np.pi
                    ,value=2.2
                    )


with col2:

    mass_ratio = st.slider("The ratio of mass between the two objects (Unitless):",
                    min_value=0.01
                    ,max_value=1.0
                    ,value=.72
                    )

    declination = st.slider("Declination (Radians):",
                    min_value= -np.pi/2 
                    ,max_value= np.pi/2
                    ,value= -1.2
                    )

with col3:

    distance = st.slider("The Luminosity distance to the GW event (Mega-Parsecs):",
                        min_value=100.0
                        ,max_value=5000.0
                        ,value=2400.0
                        )


    inclination = st.slider("Inclination angle (radians):",
                    min_value=0.0
                    ,max_value= np.pi
                    ,value=.5
                    )


with col4:
    event_time = st.slider("The detected time of the GW event:",
                min_value = datetime_center-timedelta(seconds=.1)
                ,max_value=datetime_center+timedelta(seconds=.1)
                ,value=datetime_center+timedelta(seconds=.027)
                ,step=timedelta(seconds=.001)
                ,format = "h:mm:ss.SSS"
                )


    polarization = st.slider("Polarization (Strain):",
                    min_value=0.0 
                    ,max_value= 2*np.pi
                    ,value=.01
                    )

with col5:
    phase = st.slider("Coalesence phase of the binary (radians):",
                    min_value=0.0            
                    ,max_value= 2* np.pi
                    ,value=.01
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


colors = import_colours_dict()

########################################################################



tab1, tab2, tab3 = st.tabs(["Single Detector","Two Detectors","Three Detectors"])


with tab1:
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)

    apply_gw_1_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)



with tab2:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford Model",row=2,col=1)

    apply_gw_2_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)


with tab3:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford Model",row=2,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["V1"].value,colors["V1"],"Virgo",row=3,col=1)
    add_GW_trace_subplot(fig_resampler,V1_white_template.times.value,V1_white_template.value,"black","Virgo Model",row=3,col=1)

    apply_gw_3_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)





