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
def create_pure_data():
    pure_data1 = {}
    ifos = ['L1', 'V1', 'H1']
    gps =1242442967.4

    for ifo in ifos:
        filename = f"GW190521_data/{ifo}_data_32s.hdf5"
        pure_data1[ifo] = TimeSeries.read(filename)

    return pure_data1

def import_pure_data():
    key = "pure_data"
    if key not in st.session_state:
        st.session_state[key] = create_pure_data()
    return st.session_state[key]
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def create_raw_data():

    raw_data1 = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data2 = import_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        raw_data1[ifo] = pure_data2[ifo].crop(gps-2,gps+2)

    return raw_data1

def import_raw_data():
    key = "raw_data"
    if key not in st.session_state:
        st.session_state[key] = create_raw_data()
    return st.session_state[key]
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def create_bandpass_data():

    bandpass_data1 = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data3 = import_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        bandpass_data1[ifo] = pure_data3[ifo].bandpass(25,90).crop(gps-2,gps+2)

    return bandpass_data1

def import_bandpass_data():
    key = "bandpass_data"
    if key not in st.session_state:
        st.session_state[key] = create_bandpass_data()
    return st.session_state[key]
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def create_whitend_data():

    whitend_data1 = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data4 = import_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        whitend_data1[ifo] = pure_data4[ifo].whiten(fftlength=4,overlap=2,window=('tukey',1./4.)).crop(gps-2,gps+2)

    return whitend_data1

def import_whitend_data():
    key = "whitend_data"
    if key not in st.session_state:
        st.session_state[key] = create_whitend_data()
    return st.session_state[key]
#--------------------------------------------


#--------------------------------------------
@st.cache_data
def create_GW_data():

    whitend_data2 = {}
    bandpass_data2 = {}
    GW_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data5 = import_pure_data()
    gps =1242442967.4

    for ifo in ifos:
        whitend_data2[ifo] = pure_data5[ifo].whiten(fftlength=4,overlap=2,window=('tukey',1./4.))
        bandpass_data2[ifo] = whitend_data2[ifo].bandpass(25,90)
        GW_data[ifo] = bandpass_data2[ifo].crop(gps-2,gps+2)

    return GW_data

def import_GW_data():
    key = "GW_data"
    if key not in st.session_state:
        st.session_state[key] = create_GW_data()
    return st.session_state[key]
#--------------------------------------------

@st.cache_data
def create_colours_dict():
    colours = {}
    colours['H1'] = '#ee0000' # 'gwpy:ligo-hanford'
    colours['L1'] = '#4ba6ff' # 'gwpy:ligo-livingston'
    colours['V1'] = '#9b59b6' # 'gwpy:virgo'
    return colours

def create_labels_dict():
    labels ={}
    labels['H1'] = '   Hanford'
    labels['L1'] = 'Livingston'
    labels['V1'] = '     Virgo'
    return labels

def create_short_labels_dict():
    short_labels ={}
    short_labels['H1'] = 'Hanford'
    short_labels['L1'] = 'Livingston'
    short_labels['V1'] = 'Virgo'
    return short_labels


def import_colours_dict():
    key = "colours_dict"
    if key not in st.session_state:
        st.session_state[key] = create_colours_dict()
    return dict(st.session_state[key])

def import_labels_dict():
    key = "labels_dict"
    if key not in st.session_state:
        st.session_state[key] = create_labels_dict()
    return dict(st.session_state[key])

def import_short_labels_dict():
    key = "short_labels_dict"
    if key not in st.session_state:
        st.session_state[key] = create_short_labels_dict()
    return dict(st.session_state[key])
