import streamlit as st
from gwosc.datasets import event_gps
from astropy.time import Time
from tools.plotly_templates import *
from tools.data_caching import *




st.set_page_config(page_title="Noise Correction", page_icon="📈",layout="wide")

st.title("Removing Noise")
st.write(
    "Lets take a closer look at the steps needed to remove unwanted noise from GW data."
)

st.divider()

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
ifos = ['V1', 'H1','L1']

datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

colors = load_colours_dict()

##########################################################################################################################
st.header("Removing noise with a Bandpass Filter")


blurb1 = """Since we know that the timeseries is dominated by low frequncy noise, we can easily remove a large 
part of our detector noise by filtering our data's frequencies, removing any amplitudes caused by frequencies below a 
certain frequency threashold. This is called a "high-pass" filter.

Equally, much of the high frequncy domain will contain only noise with no signal. We can remove this high frequency noise in 
the same way, applying a "low-pass" filter to remove noise caused by high frequency sources.

In practice, we apply a "Band-Pass" filter to the data, which can be thought of as a combination of our high-pass and low-pass filters,
 keeping a "band" of frequencies by removing both high and low frequency noise.

Here is the Ligo-Livingston Strain data with a suitable bandpass applied to it.
"""
st.markdown(blurb1)

col1, middle ,col2= st.columns([5,1,5],gap=None)

for ifo in ifos:
    bandpass_data[ifo] = bandpass_data[ifo].crop(gps-2,gps+2)

with col1:

    raw_fig = create_new_figure()
    plot_traces(raw_fig,raw_data,["L1"],alpha={ "L1": 1,"H1": .8,"V1": .8 })
    apply_gw_strain_layout(raw_fig,title='Unprocessed Ligo-Livingston Strain',data_range="raw")
    st.plotly_chart(raw_fig, theme="streamlit",on_select="rerun",use_container_width=True,key="noise_correction_raw")

    st.caption("An interactive plot of the unprocessed 4 second Ligo-Livingston segment that contains the GW190521 event.",help=graph_help())




with col2:

    bp_fig = create_new_figure()
    plot_traces(bp_fig,bandpass_data,["L1"],alpha={ "L1": 1,"H1": .8,"V1": .8 })
    apply_gw_strain_layout(bp_fig,title='Bandpassed Strain from Ligo-Livingston',data_range="bandpass")
    st.plotly_chart(bp_fig, theme="streamlit",on_select="rerun",use_container_width=True)

    st.caption("An interactive plot of the correctly bandpassed 4 second Ligo-Livingston segment that contains the GW190521 event.",help=graph_help())



blurb2 = """After using a bandpass to remove the both the high and low frequency noise, it is now possible to see the Strain 
peak caused by Gravitational Waves from the GW190521 event.

Although it is now possible to see the effect of the GW event, there is one more large bias that can be corrected.
"""
st.markdown(blurb2)

st.divider()
##########################################################################################################################
st.header("Whitening the data")


blurb3 = """White noise refers to noise that has the same amplitude across the entire frequency range. 

We can whiten our data using the ASD, re-weighting it so that all frequency bins have a nearly equal amount of noise.

A whitening tranformation removes correlated features while leaving variation in the data.

In this case, whitening removes the bias that comes from the detector sensitivity being frequency dependant.

It has the additional benefit of normalizing the Strain amplitude to a more regular scale.

Below is the Ligo-Livingston Strain Timeseries and ASD, as well as a toggle to see the effect of whitening the data.
"""
st.markdown(blurb3)


ifos = ['L1', 'V1', 'H1']
White_ASD_data = {}
for ifo in ifos:
    White_ASD_data[ifo] = whitend_data[ifo].asd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.)

ASD_data = load_ASD_data()
white_ASD_fig = create_new_figure()
white_ASD_timeseries_fig = create_new_figure()

white_data_for_ASD = load_whitend_data()

for ifo in ifos:
    white_data_for_ASD[ifo]  = white_data_for_ASD[ifo].crop(gps-2,gps+2)


spacing1, checkbox_col ,spacing3= st.columns([5,2,6],gap=None)

with checkbox_col:
        
    if st.checkbox("Whiten the data."):
        plot_traces(white_ASD_timeseries_fig,white_data_for_ASD,ifos=["L1"])
        apply_gw_strain_layout(white_ASD_timeseries_fig,title='Whitened Ligo-Livingston Strain',data_range="whiten")

        plot_freq_traces(white_ASD_fig,White_ASD_data,ifos=["L1"])
        apply_gw_freq_layout(white_ASD_fig,title = "Whitened Ligo-Livingston Amplitude Spectral Density(ASD)", yrange = [-2.4,-.8],ytitle="Normalized Strain/√Hz")
    else:
        plot_traces(white_ASD_timeseries_fig,raw_data,ifos=["L1"])
        apply_gw_strain_layout(white_ASD_timeseries_fig,title='Unprocessed Ligo-Livingston Strain',data_range="raw")

        plot_freq_traces(white_ASD_fig,ASD_data,ifos=["L1"])
        apply_gw_freq_layout(white_ASD_fig,title = "Ligo-Livingston Amplitude Spectral Density(ASD)", yrange = [-23.7,-19.9],ytitle="Strain/√Hz")


whiteASD_col1, middle, whiteASD_col2 = st.columns([10,1,10],gap=None)

with whiteASD_col1:

    st.plotly_chart(white_ASD_timeseries_fig, theme="streamlit",on_select="rerun",use_container_width=True)

    st.caption("An interactive plot of the 4 second segment that contains the GW190521 event.",help=graph_help())

with whiteASD_col2:

    st.plotly_chart(white_ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)

    st.caption("An interactive plot of the Amplitude Spectral Density for the GW190521 timeseries.",help=graph_help())



