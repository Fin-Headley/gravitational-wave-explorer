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


st.set_page_config(page_title="Exploring GW Data", page_icon="📈",layout="wide")

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
#ifos = ['V1', 'H1','L1']
ifos = ['L1', 'V1','H1']

datetime_center = Time(time_center, format='gps').utc.datetime

################################################################################################

blurb1 = """Before we take a look at any signal processing, we first need to collect some Gravitational Wave data.   

The Gravitational-Wave Open Science Center provides public strain data from GW Observatories that can \
be acessed with the :blue-background[gwosc] Python library. 
"""
st.markdown(blurb1)

with st.expander("Importing GW190521 Data with gwosc", expanded=False, icon=None, width="stretch"):

    with st.echo():
        from gwosc.datasets import event_gps
        from gwpy.time import from_gps

        gps_time = event_gps('GW190521')
        segment = ((gps)-16, (gps)+16)
        st.write("Time of event:", gps_time, "(GPS Seconds)")
        st.write("Time of event:",from_gps(gps_time))
        st.write("The 32 second time period centered on the GW190521 event: ",segment)

    st.divider()

    blurb2 = """We can now fetch interferometry data for the timespan that includes our GW event by using the appropriate key for a Gravitational Wave Observatory: \
        "L1", "H1", or "V1". """
    st.markdown(blurb2)

    st.code("""
    from gwpy.timeseries import TimeSeries
    Ligo_Livingston =  TimeSeries.fetch_open_data('L1', *segment)
    Ligo_Hanford    =  TimeSeries.fetch_open_data('H1', *segment)
    Virgo           =  TimeSeries.fetch_open_data('V1', *segment)""")

    with st.expander("Note on Data Storage", expanded=False, icon=None, width="stretch"):
        st.write("""The data used in this app is stored locally in hdf5 files as to not waste resources redownloading the same data over and over again.   
                The data used can be found in the GW190521_data folder in the github repository.""")

    st.divider()

    st.write("Lets take a brief a look at what type information we have about our data.")

    st.write("Data type:       :green-background[",str(type(pure_data['L1'])),"]")
    st.write("Segment duration:   :green-background[",str(pure_data['L1'].duration),"]")
    st.write("Start time: :green-background[",str(Time(pure_data['L1'].x0, format='gps').utc.datetime),"]")
    st.write("End time: :green-background[",str(Time(pure_data['L1'].times[-1], format='gps').utc.datetime),"]")
    st.write("Data Sample Rate: :green-background[",str(pure_data['L1'].sample_rate),"]")
    st.write("Data Δt:    :green-background[",str(pure_data['L1'].dt),"]")
    st.write("GW Event Time:    :green-background[",(datetime_center.strftime('%a %d %b %Y, %I:%M:%S.%f')[:-4]+datetime_center.strftime(' %p')),"]")



################################################################################################

# raw data
Pure_fig = create_new_figure()
plot_traces(Pure_fig,pure_data,ifos)
#add_event_marker(fig=Pure_fig, marker_time = datetime_center, marker_name=" Rough Time of Event", line_color="green")
apply_gw_strain_layout(Pure_fig,title='Unprocessed Gravitational Wave Strain Data',data_range="pure")
st.plotly_chart(Pure_fig, theme="streamlit",on_select="rerun",use_container_width=True)


st.caption("An interactive plot of the 32 second segment that contains the GW190521 event.",help=graph_help())


blurb3 = """This plot is almost entirely dominated by noise. The Strain amplitude waves shown above have a period of around .10 seconds,
 corresponding to ~10 Hz, most likely corresponding to seismic activity on Earth picked up by the interferometers as noise, not any 
 astrophysical events (although there are GW mergers that occur in this frequency range).

We can see this more clearly if we look at the data in a new way. Instead of plotting Strain vs time, lets use a Fourier Transform 
and look at the Strain vs frequency. One common way of examining this relationship is plotting the Amplitude Spectral Density (ASD). 

Put simply, an ASD is a measure of the of noise in the amplitude of a signal at each frequency.
"""
st.markdown(blurb3)

########################################################################################################

# PSD plot
PSD_data = load_PSD_data()
PSD_fig = create_new_figure()

ASD_data = load_ASD_data()




#plot_freq_traces(PSD_fig,PSD_data,ifos=ifos)
#apply_gw_freq_layout(PSD_fig,title = "Power Spectral Density(PSD)", yrange = [-47.3,-40],ytitle=" (Strain^2/HZ)")

#st.plotly_chart(PSD_fig, theme="streamlit",on_select="rerun",use_container_width=True)

#graph_help_wth_slider = """Use the button in the lower right to view preset ranges. 
#                        Use the slider at the bottom of the plot to manually adjust range.
#                        You can hide/show GW Observatories by clicking on their name in the legend.  
#                        Click to pan.    
#                        Change tools in the top right to use custom zooms.   
#                        Double-click to reset axis to full graph."""

#st.caption("An interactive plot of the 32 second segment that contains the GW190521 event.",help=graph_help)


ASD_data = load_ASD_data()
ASD_fig = create_new_figure()

plot_freq_traces(ASD_fig,ASD_data,ifos=ifos)
apply_gw_freq_layout(ASD_fig,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19.9],ytitle="Strain/√Hz")

st.plotly_chart(ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)

st.caption("An interactive plot of the Amplitude Spectral Density for the GW190521 timeseries.",help=graph_help())



blurb4 = """By looking at the ASD, we can clearly see spikes corresponding to high amounts of noise occurring at certain frequncies. 

As the figure is shown in logarithmic scale, it should also clear that the amount of noise is much greater at low frequncies. In fact, the the peak amplitude
for Ligo Livingston (occuring at roughly 10 Hz for all three detectors), corresponds to noise with an amplitude between 5000x and 36000x higher
than the region our GW signal is in. This makes it impossible to spot the GW signal without first taking steps to remove and correct for this unwanted noise.

"""
st.markdown(blurb4)
