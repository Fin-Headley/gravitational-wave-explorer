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
import plotly.express as px
import plotly.graph_objects as go
import datetime
import plotly
from plotly_resampler import FigureResampler # type: ignore
from datetime import timedelta
from plotly_template import *
import time
from data_caching import *
from matched_filtering_functions import *
import arviz as az
import pandas as pd
import corner

st.set_page_config(page_title="results", page_icon="📈",layout="wide")

st.title("Results:")
st.write(
    "lets take a look at my best fitting paramters!"
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

ifos = ['L1','H1']
########################################################################

#burnin = 35426 #thin = 2
#reduced_data = az.from_netcdf("MCMC_processed_data.nc")


#mcmc_df = pd.read_parquet("mcmc_df_with_log_post.parquet")
#mcmc_df.rename(inplace=True,columns={"TimeShift":"Time Shift","RA":"Right Ascension","Dec":"Declination","Incl":"Inclination","Pol":"Polarization","lp":"Log Posterior","chain":"Chain","draw":"Draw"})

MAP_df = pd.read_parquet("MAP_parameters.parquet")
MAP_df.rename(inplace=True,index={"TimeShift":"Time Shift","RA":"Right Ascension","Dec":"Declination","Incl":"Inclination","Pol":"Polarization","lp":"Log Posterior","chain":"Chain","draw":"Draw"})

results_df = MAP_df.copy()

column_dec_value = {"Mass":1,"Ratio":2,"Distance":0,"Time Shift":5,"Phase":2,"Right Ascension":4,"Declination":3,"Inclination":2,"Polarization":3}

column_titles = np.array(["Mass","Ratio","Distance","Time Shift","Phase","Right Ascension","Declination","Inclination","Polarization"])


#results_df

for i in column_titles:
    temp = results_df["MAP"].loc[i]
    temp = np.round(temp,column_dec_value[i])
    results_df["MAP"].loc[i] = temp
    temp1,temp2 = results_df["onestd"].loc[i]
    temp1 =np.round(temp1,column_dec_value[i])
    temp2 =np.round(temp2,column_dec_value[i])
    results_df["onestd"].loc[i] = (temp1, temp2)
    temp1,temp2 = results_df["twostd"].loc[i]
    temp1 =np.round(temp1,column_dec_value[i])
    temp2 =np.round(temp2,column_dec_value[i])
    results_df["twostd"].loc[i] = (temp1, temp2)

#results_df

results_col1, results_col2 = st.columns([1,3],gap=None)


def get_results(index="Mass"):

    MAP=results_df["MAP"].loc[index]
    onesig_low,onesig_high = results_df["onestd"].loc[index]
    twosig_low, twosig_high = results_df["twostd"].loc[index]
    return MAP,onesig_low, onesig_high, twosig_low, twosig_high


with st.expander("Estimates for the MCMC parameters", expanded=False, icon=None, width="stretch"):

    st.write("Here are my Maximum a posteriori estimates for each of the model paramters.")
    
    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Mass")
    st.latex(rf"""M_1={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Primary Mass")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Ratio")
    st.latex(rf"""q={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Mass Ratio")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Distance")
    st.latex(rf"""D_L={int(MAP)}^{{{int(twosig_high)}}}_{{{int(twosig_low)}}} \; (\text{{2$\sigma$}})""",help="Luminosity Distance")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Phase")
    st.latex(rf"""\phi_c={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Coalesence Phase")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Right Ascension")
    st.latex(rf"""\alpha={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Right Ascension")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Declination")
    st.latex(rf"""\delta={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Declination")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Inclination")
    st.latex(rf"""i={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Inclination")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Polarization")
    st.latex(rf"""P={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Polarization")

    #st.latex(rf"""M_1={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""q={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""D_L={int(MAP)}^{{{int(onesig_high)}}}_{{{int(onesig_low)}}} \; (\text{{1$\sigma$}}),\quad{int(MAP)}^{{{int(twosig_high)}}}_{{{int(twosig_low)}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""\phi_c={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""\alpha={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""\delta={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""i={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")
    #st.latex(rf"""P={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")


    with st.expander("Timeshift", expanded=False, icon=None, width="stretch"):
        
        st.write("Time shift was a parameter for the model, but has no physical meaning. I have included it here but it can more or less be disregarded at this point.")

        MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Time Shift")
        st.latex(rf"""TimeShift={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""",help="Time from event_gps('GW190521')")
        #st.latex(rf"""TimeShift={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")



st.subheader("MAP paramter model plotted against real data")

MAP_params = []
for i in range(9):
    MAP_params.append(results_df["MAP"].iloc[i])


MAP_template = gen_template(MAP_params)

L1_white_template = MAP_template["L1"].whiten(asd=np.sqrt(PSD_data["L1"]),highpass=25.,lowpass = 90.)
H1_white_template = MAP_template["H1"].whiten(asd=np.sqrt(PSD_data["H1"]),highpass=25.,lowpass = 90.)
V1_white_template = MAP_template["V1"].whiten(asd=np.sqrt(PSD_data["V1"]),highpass=25.,lowpass = 90.)

colors = import_colours_dict()

tab1, tab2, tab3 = st.tabs(["Single Detector","Two Detectors","Three Detectors"])


with tab1:
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    apply_gw_1_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)



with tab2:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford MAP Model",row=2,col=1)

    apply_gw_2_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)


with tab3:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford MAP Model",row=2,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["V1"].value,colors["V1"],"Virgo",row=3,col=1)
    add_GW_trace_subplot(fig_resampler,V1_white_template.times.value,V1_white_template.value,"black","Virgo MAP Model",row=3,col=1)

    apply_gw_3_model_comparision_layout(fig_resampler,title='GW Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)




pure_data = import_pure_data()
raw_data = import_raw_data()
bandpass_data = create_bandpass_data()
whitend_data = create_whitend_data()
GW_data = import_GW_data()
PSD_data = import_PSD_data()

SNRs = {}
ifos = ['L1','H1','V1']
colours = import_colours_dict()

labels = import_labels_dict()

for ifo in ifos:
    template = MAP_template[ifo]
    cropped_data = pure_data[ifo].crop(time_center - 2,time_center + 2)

    # FFT of the data, with the appropriate normalisation
    data_f=cropped_data.average_fft(window=('tukey',1./4.))*(cropped_data.duration/2)

    # FFT of the template, with the appropriate normalisation
    template_f=template.average_fft(window=('tukey',1./4.))*(template.duration/2)

    # We will need the PSD with the same frequency spacing as the data and template,
    # so we interpolate it to match:
    Pxx=PSD_data[ifo].interpolate(data_f.df.value)

    # With the right normalisation, this is equation 7.58 of the textbook:
    optimal=data_f*template_f.conjugate()/Pxx
    opt_time=2*optimal.ifft()*(optimal.df*2)

    # This is equation 7.49 of the textbook: the overlap of the template with itself
    sigmasq = 4 * np.real((template_f * template_f.conjugate() / Pxx).sum() * template_f.df)
    sigma = np.sqrt(np.abs(sigmasq))

    # And now we have the SNR time series:
    SNR_complex = opt_time/sigma

    # We can recenter thing with the location of peak in the template:
    peaksample = template.argmax()  
    SNR_complex = np.roll(SNR_complex,peaksample)
    SNRs[ifo] = abs(SNR_complex)

    SNRmax=SNRs[ifo].max().value
    time_max=SNRs[ifo].times[SNRs[ifo].argmax()]
    st.write('Maximum {} SNR of {} at {}.'.format(ifo,SNRmax,time_max))

    #plt.plot(SNR.times,SNR,color=colours[ifo],label=labels[ifo])
    #plt.legend()
    #plt.show()


fig = go.Figure()
#make_subplots(rows=1, cols=3, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
fig_resampler = FigureResampler(fig)

#plot_traces(fig_resampler,SNRs,ifos)

fig = make_subplots(rows=1, cols=3, shared_xaxes=True, horizontal_spacing=.01 ,vertical_spacing=0.05,shared_yaxes=True,column_titles=[labels["L1"]+" SNR",labels["H1"]+" SNR",labels["V1"]+" SNR"])
fig_resampler = FigureResampler(fig)

add_GW_trace_subplot(fig_resampler,SNRs["L1"].times.value,SNRs["L1"].value,colours["L1"],labels["L1"],row=1,col=1)
add_GW_trace_subplot(fig_resampler,SNRs["H1"].times.value,SNRs["H1"].value,colours["H1"],labels["H1"],row=1,col=2)
add_GW_trace_subplot(fig_resampler,SNRs["V1"].times.value,SNRs["V1"].value,colours["V1"],labels["V1"],row=1,col=3)


st.plotly_chart(fig_resampler,use_container_width=False)

#for ifo in ifos:
#    plt.plot(SNRs[ifo].times,SNRs[ifo],color=colours[ifo],label=labels[ifo])
#    plt.legend()
#    plt.show()






