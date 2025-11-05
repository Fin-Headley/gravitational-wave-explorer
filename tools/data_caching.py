import streamlit as st
import numpy as np
from gwpy.timeseries import TimeSeries

#--------------------------------------------
@st.cache_data
def load_pure_data()-> dict:
    """
    Load unprocessed TimeSeries strain data for gravitational wave interferometers.
    
    Returns a dictionary containing unprocessed TimeSeries strain data for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. The dictionary 
    is cached by Streamlit, so subsequent calls within a session return the cached data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing unprocessed 
        interferometer TimeSeries strain data.
        
    Notes
    -----
    This function loads data from GW190521 event files located in the 
    'GW190521_data/' directory. Each file contains 32 seconds of strain data.
    """
    pure_data = {}
    ifos = ['L1', 'V1', 'H1']

    for ifo in ifos:
        filename = f"GW190521_data/{ifo}_data_32s.hdf5"
        pure_data[ifo] = TimeSeries.read(filename)

    return pure_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_raw_data()-> dict:
    """
    Load cropped TimeSeries strain data around the GW190521 gravitational wave event.
    
    Returns a dictionary containing 4-second segments of TimeSeries strain data 
    for the Livingston (L1), Hanford (H1), and Virgo (V1) interferometers, cropped 
    to ±2 seconds around the GW190521 event time. The dictionary is cached by 
    Streamlit, so subsequent calls within a session return the cached data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing cropped 
        interferometer TimeSeries strain data, each spanning 4 seconds 
        (±2 seconds around the GW190521 event).
        
    Notes
    -----
    This function uses the GW190521 event GPS time (1242442967.4) to crop 
    the data from 2 seconds before to 2 seconds after the event. The raw 
    data is obtained by calling load_pure_data() and then cropping each 
    interferometer's data to the 4-second window of interest.
    """
    raw_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    gps =1242442967.4 #gps time of GW190521 event

    for ifo in ifos:
        raw_data[ifo] = pure_data[ifo].crop(gps-2,gps+2)

    return raw_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_bandpass_data()-> dict: 
    """
    Load bandpass-filtered TimeSeries strain data for gravitational wave interferometers.
    
    Returns a dictionary containing bandpass-filtered TimeSeries strain data for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. The data is 
    filtered to retain frequencies between 25-90 Hz, which is the frequency 
    range I found to be best for the GW190521 event. The dictionary is cached 
    by Streamlit, so subsequent calls within a session return the cached data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing bandpass-filtered 
        interferometer TimeSeries strain data with frequencies between 25-90 Hz.
        
    Notes
    -----
    This function applies a bandpass filter with a frequency range of 25-90 Hz 
    to the unprocessed data obtained from load_pure_data().
    """
    bandpass_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        bandpass_data[ifo] = pure_data[ifo].bandpass(25,90)

    return bandpass_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_whitend_data()-> dict:
    """
    Load whitened TimeSeries strain data for gravitational wave interferometers.
    
    Returns a dictionary containing whitened TimeSeries strain data for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. Whitening 
    is performed using the amplitude spectral density (ASD) derived from the 
    power spectral density (PSD) data. The dictionary is cached by Streamlit, so 
    subsequent calls within a session return the cached data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing whitened 
        interferometer TimeSeries strain data normalized by detector 
        noise characteristics.
        
    Notes
    -----
    This function performs whitening by dividing the strain data by the 
    amplitude spectral density (ASD), which is calculated as the square 
    root of the power spectral density (PSD) obtained from load_PSD_data().
    """
    whitend_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()
    PSD_data = load_PSD_data()

    for ifo in ifos:
        whitend_data[ifo] = pure_data[ifo].whiten(asd=np.sqrt(PSD_data[ifo]))

    return whitend_data
#--------------------------------------------


#--------------------------------------------
@st.cache_data
def load_GW_data()-> dict:
    """
    Load fully processed gravitational wave strain data ready for analysis.
    
    Returns a dictionary containing preprocessed TimeSeries strain data for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. The dictionary 
    is cached by Streamlit, so subsequent calls within a session return the cached 
    data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing fully processed 
        interferometer TimeSeries strain data.
        
    Notes
    -----
    This function combines the complete gravitational wave data processing pipeline.
    Unprocessed data is obtained from load_pure_data() and the ASD for whitening is
    calculated using the square root of the PSD, obtained from load_PSD_data().
    """
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
def load_ASD_data()-> dict:
    """
    Load amplitude spectral density (ASD) data for gravitational wave interferometers.
    
    Returns a dictionary containing amplitude spectral density estimates for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. The dictionary 
    is cached by Streamlit, so subsequent calls within a session return the cached data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing amplitude spectral 
        density FrequencySeries data for each interferometer.
        
    Notes
    -----
    The unprocessed data is obtained from load_pure_data().

    The ASD is computed using Welch's method with the following parameters:
    - FFT length: 4 seconds
    - Window: Tukey window with α=0.25
    - Method: Welch's method
    - Overlap: 2 seconds (50% overlap)
    """
    ASD_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        ASD_data[ifo] = pure_data[ifo].asd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.) # type: ignore

    return ASD_data
#--------------------------------------------






#--------------------------------------------
@st.cache_data
def load_PSD_data()-> dict:
    """
    Load power spectral density (PSD) data for gravitational wave interferometers.
    
    Returns a dictionary containing power spectral density estimates for the 
    Livingston (L1), Hanford (H1), and Virgo (V1) interferometers. The dictionary 
    is cached by Streamlit, so subsequent calls within a session return the cached 
    data.

    Returns
    -------
    dict
        Dictionary with keys ['L1', 'V1', 'H1'] containing power spectral 
        density FrequencySeries data for each interferometer, (representing 
        the squared amplitude of detector noise as a function of frequency).
        
    Notes
    -----
    The unprocessed data is obtained from load_pure_data().

    The PSD is computed using Welch's method with the following parameters:
    - FFT length: 4 seconds
    - Window: Tukey window with α=0.25
    - Method: Welch's method
    - Overlap: 2 seconds (50% overlap)
    """
    PSD_data = {}
    ifos = ['L1', 'V1', 'H1']
    pure_data = load_pure_data()

    for ifo in ifos:
        PSD_data[ifo] = pure_data[ifo].psd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.) # type: ignore

    return PSD_data
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_colours_dict()-> dict[str, str]:
    """Return a dictionary mapping interferometer keys to their standard plotting colors."""
    colours = {}
    colours['H1'] = '#ee0000' # 'gwpy:ligo-hanford'
    colours['L1'] = '#4ba6ff' # 'gwpy:ligo-livingston'
    colours['V1'] = '#9b59b6' # 'gwpy:virgo'
    return colours
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_labels_dict()-> dict[str, str]:
    """Return a dictionary mapping interferometer keys to formatted display labels."""
    labels ={}
    labels['H1'] = '   Hanford'
    labels['L1'] = 'Livingston'
    labels['V1'] = '     Virgo'
    return labels
#--------------------------------------------

#--------------------------------------------
@st.cache_data
def load_short_labels_dict()-> dict[str, str]:
    """Return a dictionary mapping interferometer keys to short display labels."""
    short_labels ={}
    short_labels['H1'] = 'Hanford'
    short_labels['L1'] = 'Livingston'
    short_labels['V1'] = 'Virgo'
    return short_labels
#--------------------------------------------
