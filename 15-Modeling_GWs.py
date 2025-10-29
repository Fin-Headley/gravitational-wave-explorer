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
########################################################################

st.title("How to we model Gravitational waves?")

st.markdown(
'''
This will by no means be a comprehensive guide, but I will try and give a brief overview.

Black Hole Mergers take place over three distinct phases.

:blue-background[Inspiral Stage]: The two Black Holes circle each other from afar. The amplitude of the emitted Gravitational Waves 
slowly build up over time as the objects get closer together.

:blue-background[Merger Stage]: The two Black Holes come together and **coalesce** into one object.

:blue-background[Ringdown Stage]: The newly formed Black Hole settles into its new state, and the Gravitational Wave signal falls away.

A description of the complete evolution requires solving the full equations of general relativity, 
a task which is often impossible to do analytically. 

With modern techniques it is possible to model a Binary Black Hole Merger using Numerical Relativity (NR), 
although it is prohibitively expensive to do a full NR simulation for every GW model.

Using a combination of other techniques (Post-Newtonian approximations and Perturbation Theory) as well as mathematical 
approximations, it is possible to create models that simulate the resulting Gravitational Wave Signal. 

I will focus on showcasing how to use one such model here.
''')

st.divider()

st.write("For my modeling I used the 'SEOBNRv4_opt' model, some random sample parameters are shown bellow.")

st.code("""
from pycbc.waveform import get_td_waveform

hp, hc = get_td_waveform(approximant="SEOBNRv4_opt",
                            mass1=50,               #Primary Black Hole Mass (in Solar Masses)
                            mass2=20,               #Secondary Black Hole Mass (in Solar Masses)
                            distance=2000,          #Luminosity distance to the Merger (in Mega-Parsecs)
                            inclination=1.2,        #inclination angle of the Merger (radians)
                            coa_phase=.4,           #Coalesence phase of the binary (radians)
                            delta_t=0.000244140625, #Timestep of the output Timeseries (Seconds)
                            f_lower=30)             #Lowest Frequency that will be modeled (Hz)

        
#The get_td_waveform() function produces an outputs for both the plus polarization and cross polarization
#of the modeled Gravitational Wave event, defined here as hp and hc
""")

st.write("The two output waveforms for the above parameters are plotted below:")

hp, hc = get_td_waveform(approximant="SEOBNRv4_opt",
                            mass1=50,               #Primary Black Hole Mass (in Solar Masses)
                            mass2=20,               #Secondary Black Hole Mass (in Solar Masses)
                            distance=2000,          #Luminosity distance to the Merger (in Mega-Parsecs)
                            inclination=1.2,        #inclination angle of the Merger (radians)
                            coa_phase=.4,           #Coalesence phase of the binary (radians)
                            delta_t=0.000244140625, #Timestep of the output Timeseries (Seconds)
                            f_lower=30)             #Lowest Frequency that will be modeled (Hz)

polarization_plot = create_new_figure()

polarization_plot.add_trace(go.Scatter(
            mode='lines',
            line_color="green",
            showlegend=True,
            name="Plus polarization",
            opacity= 1
        ),
        hf_x = hp.get_sample_times(),
        hf_y = hp,
        limit_to_view=True,
        max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )

polarization_plot.add_trace(go.Scatter(
            mode='lines',
            line_color="orange",
            showlegend=True,
            name="Cross polarization",
            opacity= 1
        ),
        hf_x = hc.get_sample_times(),
        hf_y = hc,
        limit_to_view=True,
        max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )

polarization_plot.update_layout(
    # Hover settings
    hovermode='x unified',
    #hoversubplots="axis",
    width=400,
    height=400,

    # Title settings
    title={
        'text': "CBC Model Output",
        'y': 0.9,
        'x': .5,
        'xanchor': 'center',
        'yanchor': 'top',
        'automargin': True
    },
    
    # Y-axis settings
    yaxis=dict(
        title="Strain",
        fixedrange=False,
        showexponent="all",
        exponentformat="power",
        hoverformat=".3e",
        mirror=True,
        side='left',
        linewidth=1, linecolor="black", showline=True,
        showgrid=True,
    ),

    # X-axis settings
    xaxis=dict(
        #rangeslider=dict(visible=True),
        title="Time (seconds)",
        #type="date",
        #nticks=8,
        showgrid=True,
        #hoverformat="Time: %H:%M:%S.%3f",
        autotickangles = [0],
        linewidth=1, linecolor='black', mirror=True, showline=True,
        domain=[0, 0.98]
    ),
    
    # Legend settings
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.0,
        xanchor="right",
        x=.98,
        borderwidth=1, bordercolor='black',
    ),
)
polarization_plot.update_yaxes(showline=True, mirror=True, linecolor="black", linewidth=1)
st.plotly_chart(polarization_plot, theme="streamlit",on_select="rerun",use_container_width=True)

st.caption("An interactive plot of an example get_td_waveform() CBC model.",help=graph_help_no_buttons())

blurb1 = """
There are several things to note about the above plot.

1. The merger is centered at 0 seconds, with an insprial whos length is defined by f_lower, and an ringdown that ends with a Strain Amplitude of 0.
2. The overall Strain Amplitude is in the ballpark of what we would expect to see for an unwhitened and unormalized strain.
3. The Plus and Cross polarization can have different Amplitudes.
"""
st.markdown(blurb1)

blurb2 = """
In order to compare our model to real data, we will need transform this waveform into a detector specific 
CBC template, taking into account that the interferometers point in different directions and are in different locations
on the Earth. This means that we have to take into account each detector's sensitivity to the different polarizations 
(due to the position and layout of each interferometer), as well as the time difference in when each detector would recieve
the GW signal.
"""
st.markdown(blurb2)


st.write("I acomplished this by defining a generate_template function, which  first used get_td_waveform " \
"to get the plus and crosspolarizations, before transforming the waveform to match the appropriate detector responce.")

with st.expander("The gen_template() function:"):
    st.code(
    """
    from gwosc.datasets import event_gps
    from gwpy.time import from_gps
    from gwpy.timeseries import TimeSeries
    from pycbc.waveform import get_td_waveform
    from pycbc.detector import Detector

    gps_time = event_gps('GW190521')
    segment = ((gps)-2, (gps)+2)        #get a 2 second long segment containing the GW190521 event

    data = {}     #create a dictionary to hold the timeseries arrays
    data['L1'] =  TimeSeries.fetch_open_data('L1', *segment) #Ligo_Livingston
    data['H1'] =  TimeSeries.fetch_open_data('H1', *segment) #Ligo_Hanford
    data['V1'] =  TimeSeries.fetch_open_data('V1', *segment) #Virgo

    ifos = ['L1', 'V1','H1'] #A list of the three detectors to iterate over

    det={}             #create a dictionary to hold the Detector information to use in gen_template
    for ifo in ifos:
        det[ifo]=Detector(ifo)

    def gen_template(param,                                # A parameter list so that I can input a set of parameters at a time
                    gps_time = time_center,                # The time of the GW event        (used to shift models correct time)
                    delta_t =  data['H1'].dt.value,        # Assuming all detectors have the same dt         (True in this case)
                    duration=  data['H1'].duration.value,  # Assuming all detectors have the same duration   (True in this case)
                    start_time=data['H1'].x0.value,        # Assuming all detectors have the same start time (True in this case)
                    f_lower=10.):                          # Lowest Frequency that will be modeled (Hz)

        #extracting parameters from the input list
        m1, q, distance, time_shift, phase, right_ascension, declination, inclination, polarization = param 
        
        #parameters:
        #m1:                Primary Black Hole Mass (Solar Masses)
        #q:                 Mass ratio between Primary and Secondary Mass (q = m1/m2)
        #time_shift:        A variable that shifts the time the GW event is detected for all detectors (seconds) 
        #phase:             Coalesence phase of the binary (radians)
        #right_ascension    Right Ascension (sky location) of GW event (Radians)
        #declination        Declination (sky location) of GW event (Radians)
        #inclination        Inclination angle of the Merger (radians)
        #polarization       Strain Polarization (radians)

        time = gps_time + time_shift    #getting the time that will be used to align the models
        m2 = m1 * q                     #extracting the secondary mass from the primary mass and mass ratio

        hp, hc = get_td_waveform(approximant="SEOBNRv4_opt",
                                    mass1=m1,               #Primary Black Hole Mass (in Solar Masses)
                                    mass2=m2,               #Secondary Black Hole Mass (in Solar Masses)
                                    distance=distance,      #Luminosity distance to the Merger (in Mega-Parsecs)
                                    inclination=inclination,#inclination angle of the Merger (radians)
                                    coa_phase=phase,        #Coalesence phase of the binary (radians)
                                    delta_t=delta_t,        #Timestep of the output Timeseries (Seconds)
                                    f_lower=f_lower)        #Lowest Frequency that will be modeled (Hz)
        
        hp = hp*get_window(('tukey',1/4),hp.shape[0]) #apply a window to the GW polarization phases
        hc = hc*get_window(('tukey',1/4),hc.shape[0]) #this helps remove effects caused by discontinous jumps in frequency

        # Resize the internal signal buffer so the model polarizations are the same size as the data duration
        hp.resize(int(duration/delta_t))
        hc.resize(int(duration/delta_t))
        
        ht={}           #a dictionary used to calculate the detector simulated detector strain of the model 
        template={}     #a dictionary with the final CBC model templates

        # compute the detectors responses and shift to the requested time

        for ifo in ifos: #for each detector
        
            #calculate the detector responce
            fp, fc = det[ifo].antenna_pattern(right_ascension, declination, polarization, time) 
            ht[ifo] = fp * hp.copy() + fc * hc.copy()
            
            #find the time delay due to geographic
            time_delay = det[ifo].time_delay_from_earth_center(right_ascension, declination, time) 
            
            #shift the detector responce to the appropriate starting time
            ht[ifo] = ht[ifo].cyclic_time_shift(ht[ifo].start_time + time - start_time + time_delay) 
            ht[ifo].start_time=start_time 
        
            #save the TimeSeries in the output dictionary
            template[ifo]=TimeSeries.from_pycbc(ht[ifo])

        return template #return the correct CBC model strain for each detector
    """
    )


st.divider()


param_example = [50., 50./20., 2000, .01 ,.4, 1.2,.97,1.2,1.3]
#m1, q, distance, time_shift, phase, right_ascension, declination, inclination, polarization


st.write("Using the gen_template() function, and explanding on the same example parameters as before, we can plot our CBC model as it would be seen by each Interferometer.")

ifos = ['H1','L1', 'V1']


st.code(
"""
#all prior variables chosen to be the same
mass = 50.
q = 50./20.
distance = 2000
time_shift = .01        #randomly chosen close to 0
phase = .4              
right_ascension = 1.2   #randomly chosen
declination = .97       #randomly chosen
inclination = 1.2
polarization = 1.3      #randomly chosen

param_list = [50., 50./20., 2000, .01 ,.4, 1.2,.97,1.2,1.3] 

example_template = gen_template(param_list,
                 gps_time = 1141440002.,    #randomly chosen
                 delta_t =  0.000244140625, 
                 duration=  4.0,            
                 start_time=1141440000,     
                 f_lower=30.)

plot(example_template)
"""
)

example_template = gen_template(param_example,
                 gps_time = 1141440002.,
                 delta_t =  0.000244140625, # Assuming all detectors have the same dt(I checked this to be true)
                 duration=  4.0, # Assuming all detectors have the same duration (I checked this to be true)
                 start_time=1141440000,# Assuming all detectors have the same start time (I checked this to be true)
                 f_lower=30.)

example_plot = create_new_figure()

plot_traces(example_plot,example_template,ifos)

apply_gw_strain_layout(example_plot, title = "Example Gravitational Wave models", datetime_center = Time(1141440002., format='gps').utc.datetime, data_range = "example_model")
st.plotly_chart(example_plot, theme="streamlit",on_select="rerun",use_container_width=True)
st.caption("An interactive plot of the example CBC model as it would be seen by Ligo and Virgo (assuming there is no noise).",help=graph_help())
