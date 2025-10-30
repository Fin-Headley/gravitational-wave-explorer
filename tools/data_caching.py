import streamlit as st
import numpy as np
from gwosc.datasets import find_datasets
from gwosc.datasets import event_gps
from gwpy.time import to_gps
from gwpy.time import from_gps
from pycbc.detector import Detector
from gwpy.timeseries import TimeSeries
from astropy.time import Time
import datetime
import plotly.graph_objects as go

#--------------------------------------------
@st.cache_data
def load_pure_data():
    pure_data = {}
    ifos = ['L1', 'V1', 'H1']
    gps =1242442967.4

    for ifo in ifos:
        filename = f"GW190521_data/{ifo}_data_32s.hdf5"
        pure_data[ifo] = TimeSeries.read(filename)

    return pure_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_raw_data():
    raw_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        raw_data[ifo] = pure_data[ifo].crop(gps-2,gps+2)

    return raw_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_bandpass_data(): #could change this to allow me putting my own bandpass range in
    bandpass_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        bandpass_data[ifo] = pure_data[ifo].bandpass(25,90)#.crop(gps-2,gps+2)

    return bandpass_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_whitend_data():

    whitend_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4
    PSD_data = load_PSD_data()

    for ifo in ifos:
        whitend_data[ifo] = pure_data[ifo].whiten(asd=np.sqrt(PSD_data[ifo]))#.crop(gps-2,gps+2)

    return whitend_data
#--------------------------------------------


#--------------------------------------------
@st.cache_data
def load_GW_data():

    whitend_data = {}
    bandpass_data = {}
    GW_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4
    PSD_data = load_PSD_data()

    for ifo in ifos:
        bandpass_data[ifo] = pure_data[ifo].bandpass(25,90)
        whitend_data[ifo] = bandpass_data[ifo].whiten(asd=np.sqrt(PSD_data[ifo]))
        GW_data[ifo] = whitend_data[ifo].crop(gps-2,gps+2)

    return GW_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_ASD_data():
    ASD_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        ASD_data[ifo] = pure_data[ifo].asd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.)

    return ASD_data
#--------------------------------------------






#--------------------------------------------
@st.cache_data
def load_PSD_data():
    PSD_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        PSD_data[ifo] = pure_data[ifo].psd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.)

    return PSD_data
#--------------------------------------------


#--------------------------------------------
@st.cache_data
def load_tukey_PSD_data():

    tukey_Pxx = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        tukey_Pxx[ifo] = pure_data[ifo].psd(fftlength=4.,window=('tukey',1./4.))

    return tukey_Pxx
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_nowindow_PSD_data():

    nowin_Pxx = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        nowin_Pxx[ifo] = pure_data[ifo].psd(fftlength=4.,window='boxcar')

    return nowin_Pxx
#--------------------------------------------


#--------------------------------------------
@st.cache_data
def load_colours_dict():
    colours = {}
    colours['H1'] = '#ee0000' # 'gwpy:ligo-hanford'
    colours['L1'] = '#4ba6ff' # 'gwpy:ligo-livingston'
    colours['V1'] = '#9b59b6' # 'gwpy:virgo'
    return colours
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_labels_dict():
    labels ={}
    labels['H1'] = '   Hanford'
    labels['L1'] = 'Livingston'
    labels['V1'] = '     Virgo'
    return labels
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_short_labels_dict():
    short_labels ={}
    short_labels['H1'] = 'Hanford'
    short_labels['L1'] = 'Livingston'
    short_labels['V1'] = 'Virgo'
    return short_labels
#--------------------------------------------
