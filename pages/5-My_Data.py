import streamlit as st
from gwosc.datasets import event_gps
from astropy.time import Time
from tools.plotly_templates import *
from tools.data_caching import *



st.set_page_config(page_title="My Processed Data", page_icon="📈",layout="wide")

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

for ifo in ifos:
    bandpass_data[ifo] = bandpass_data[ifo].crop(gps-2,gps+2)
    whitend_data[ifo]  = whitend_data[ifo].crop(gps-2,gps+2)

colors = load_colours_dict()


##########################################################################################################################



st.title("My processed strain data")
st.write(
    "Before we move on to modeling Gravitational Waves, here is my processed detector Strain data." \
    " This is what later models will be comparing against."
)


st.subheader("Importing Data from gwosc")

blurb1 = """I fetched Strain data for the 32 second time segment centered on the GW190521 event as described in the :grey-background[Exploring GW Data] tab.
"""
st.markdown(blurb1)



graph_col11, spacer, graph_col12 = st.columns([10,1,10],gap=None)


with graph_col11:

    Pure_fig = create_new_figure()
    plot_traces(Pure_fig,pure_data,ifos)
    apply_gw_strain_layout(Pure_fig,title='Unprocessed Gravitational Wave Strain Data',data_range="pure")
    st.plotly_chart(Pure_fig, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("An interactive plot of the unprocessed 32 second segment that contains the GW190521 event.",help=graph_help())


with graph_col12:
    ASD_data = load_ASD_data()
    ASD_fig = create_new_figure()

    plot_freq_traces(ASD_fig,ASD_data,ifos=ifos)
    apply_gw_freq_layout(ASD_fig,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19.9],ytitle="Strain/√Hz")

    st.plotly_chart(ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("An interactive plot of the Amplitude Spectral Density for the GW190521 timeseries.",help=graph_help())


st.subheader("Looking at frequency plots")

blurb2 = """I took the three Strain Timeseries and used fourier transforms to convert the time series data into a set of frequency series.
I used this to find the Amplitude Spectral Density of each detector."""

st.markdown(blurb2)

text_col1,spacer, text_col2 = st.columns([10,1,10],gap=None)

with text_col1:
    st.subheader("Using the ASD to help bandpass")
    blurb3 = """
    I used the ASD to find a suitable bandpass for the data. My final bandpass kept frequencies between 25Hz and 90Hz.
    """
    st.markdown(blurb3)
    st.markdown(" ")

with text_col2:
    st.subheader("Using the ASD to whiten the data")

    blurb4 = """
    I used the ASD to whiten the bandpassed strain data. This Bandpassed, Whitened, (and cropped) data was what I compare models against in later plots.
    """

    st.markdown(blurb4)


graph_col21, spacer, graph_col22 = st.columns([10,1,10],gap=None)



with graph_col21:
    ifos = ['H1','V1','L1']

    bp_fig = create_new_figure()
    plot_traces(bp_fig,bandpass_data,ifos)
    apply_gw_strain_layout(bp_fig,title='Bandpassed Gravitational Wave Strain Data',data_range="bandpass")
    st.plotly_chart(bp_fig, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("An interactive plot of the bandpassed 4 second segment that contains the GW190521 event.",help=graph_help())


with graph_col22:

    ifos = ['L1', 'H1','V1']
    GW_fig = create_new_figure()
    plot_traces(GW_fig,GW_data,ifos)
    apply_gw_strain_layout(GW_fig,title='Whitened and Bandpassed GW Strain Data',data_range="GW_data")
    st.plotly_chart(GW_fig, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("An interactive plot of the bandpassed and whitened 4 second segment that contains the GW190521 event.",help=graph_help())


blurb5 = """
Now that we have suitable data, with much of the noise removed, we can look at modeling Gravitational Wave events.
"""

st.markdown(blurb5)

