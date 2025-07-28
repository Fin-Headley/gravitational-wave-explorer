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


st.set_page_config(page_title="Testpage2", page_icon="📈")

st.title("testpage2")
st.write(
    "this is a test page 2."
)

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
st.write("Time of event:",gps)
st.write("Time of event:",from_gps(gps))
segment = ((gps)-16, (gps)+16)
st.write("Period of time with event in it:",segment)

time_center = gps



data = {}

ifos = ['L1', 'V1', 'H1']

for ifo in ifos:
    filename = f"/GW190521_data/{ifo}_data_32s.hdf5"
    data[ifo] = TimeSeries.read(filename)


colours = {}
colours['H1'] = 'gwpy:ligo-hanford'
colours['L1'] = 'gwpy:ligo-livingston'
colours['V1'] = 'gwpy:virgo'

labels ={}
labels['H1'] = 'LIGO-Hanford'
labels['L1'] = 'LIGO-Livingston'
labels['V1'] = 'Virgo'

ldata = data['L1']
hdata = data['H1']
vdata = data['V1']

st.write("Data type:       ", type(ldata))
st.write("Data duration:   ",ldata.duration)
st.write("Data Sample Rate:",ldata.sample_rate)
st.write("Data delta t:    ",ldata.dt)
st.write("Data start time: ",ldata.x0)

plot = GWPlot(figsize=(12, 4.8))
ax = plot.add_subplot(xscale='auto-gps')

for ifo in ifos:
    ax.plot(data[ifo],label=labels[ifo],color=colours[ifo])

ax.set_epoch(time_center) # type: ignore

ax.set_title('GW Strain data from our three Detectors')
ax.set_ylabel('Strain noise')
ax.legend(loc="best")
plt.show()
