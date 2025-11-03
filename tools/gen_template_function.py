from gwosc.datasets import event_gps
from pycbc.waveform import get_td_waveform
from pycbc.detector import Detector
from gwpy.timeseries import TimeSeries
from scipy.signal import get_window
from astropy.time import Time
from tools.plotly_templates import *
from tools.data_caching import *

pure_data = load_pure_data()
raw_data = load_raw_data()
bandpass_data = load_bandpass_data()
whitend_data = load_whitend_data()
GW_data = load_GW_data()

PSD_data = load_PSD_data()


gps = event_gps('GW190521')
time_center = gps
datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

ifos = ['L1', 'V1','H1']
########################################################################
det={}
for ifo in ifos:
    det[ifo]=Detector(ifo)

def gen_template(param,
                 gps_time = time_center,
                 delta_t =  raw_data['H1'].dt.value, # Assuming all detectors have the same dt(I checked this to be true)
                 duration=  raw_data['H1'].duration.value, # Assuming all detectors have the same duration (I checked this to be true)
                 start_time=raw_data['H1'].x0.value,# Assuming all detectors have the same start time (I checked this to be true)
                 f_lower=10.):
    
    m1, q, distance, time_shift, phase, right_ascension, declination, inclination, polarization = param
    time = gps_time + time_shift
    m2 = m1 * q

    hp, hc = get_td_waveform(approximant="SEOBNRv4_opt",
                             mass1=m1,
                             mass2=m2,
                             distance=distance,
                             inclination=inclination,
                             coa_phase=phase,
                             delta_t=delta_t,
                             f_lower=f_lower) 
    
    hp = hp*get_window(('tukey',1/4),hp.shape[0]) 
    hc = hc*get_window(('tukey',1/4),hc.shape[0]) 

    # Resize the signal buffer
    hp.resize(int(duration/delta_t))
    hc.resize(int(duration/delta_t))
    
    ht={}
    template={}
    # compute the detectors responses and shift to the requested time
    for ifo in ifos:
        fp, fc = det[ifo].antenna_pattern(right_ascension, declination, polarization, time)
        ht[ifo] = fp * hp.copy() + fc * hc.copy()
        
        time_delay = det[ifo].time_delay_from_earth_center(right_ascension, declination, time)
        
        ht[ifo] = ht[ifo].cyclic_time_shift(ht[ifo].start_time + time - start_time + time_delay)
        ht[ifo].start_time=start_time
    
        template[ifo]=TimeSeries.from_pycbc(ht[ifo])

    return template


