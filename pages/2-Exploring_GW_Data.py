import streamlit as st
from gwosc.datasets import event_gps
from gwpy.time import from_gps
from astropy.time import Time
from tools.plotly_templates import *
from tools.data_caching import *

st.set_page_config(page_title="Exploring GW Data", page_icon="📈",layout="wide")

st.title("Gravitational Wave Data")

pure_data = load_pure_data()
raw_data = load_raw_data()
bandpass_data = load_bandpass_data()
whitend_data = load_whitend_data()
GW_data = load_GW_data()


#code
gps = event_gps('GW190521')
time_center = gps
#ifos = ['V1', 'H1','L1']
ifos = ['L1', 'V1','H1']

datetime_center = Time(time_center, format='gps').utc.datetime # pyright: ignore[reportAttributeAccessIssue]

################################################################################################

blurb1 = """
Before we take a look at any signal processing, we first need to collect some Gravitational Wave data.   

The Gravitational-Wave Open Science Center provides public data from GW Observatories that can
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

st.write('We now have data from three GW Interferometers that should include a GW event!')

st.write("Lets take a look at what we know about our data. The following is information about the data we pulled from LIGO Hanford:")

col1, col2 = st.columns(2)

with col1:
    st.write("Type:       :red-background[",str(type(pure_data['H1'])),"]")
    st.write("Name:       :red-background[",pure_data['H1'].name,"]")
    st.write("Segment duration:   :red-background[",str(pure_data['H1'].duration),"]")
    st.write("Start time: :red-background[",str(Time(pure_data['H1'].x0, format='gps').utc.datetime),"]") # pyright: ignore[reportAttributeAccessIssue]
    st.write("Data Sample Rate: :red-background[",str(pure_data['H1'].sample_rate),"]")
    st.write("First value:       :red-background[",(str(pure_data['H1'].value[0])),"]")


with col2:
    st.write("dtype:       :red-background[",str(pure_data['H1'].dtype),"]")
    st.write("Unit:       :red-background[",((pure_data['H1'].unit)),"]")
    st.write("GW Event Time:    :red-background[",(datetime_center.strftime('%a %d %b %Y, %I:%M:%S.%f')[:-4]+datetime_center.strftime(' %p')),"]")
    st.write("End time: :red-background[",str(Time(pure_data['H1'].times[-1], format='gps').utc.datetime),"]") # pyright: ignore[reportAttributeAccessIssue]
    st.write("Data Δt:    :red-background[",str(pure_data['H1'].dt),"]")
    st.write("Array length:    :red-background[",str(len(pure_data['H1'].times)),"]")

################################################################################################

blurb3 = """
Lets plot the data from the three interferometers and see what it looks like.
"""
st.markdown(blurb3)


# raw data
Pure_fig = create_new_figure()
plot_traces(Pure_fig,pure_data,ifos)
apply_gw_strain_layout(Pure_fig,title='Unprocessed Gravitational Wave Strain Data',data_range="pure")
st.plotly_chart(Pure_fig, theme="streamlit",on_select="rerun",use_container_width=True)


st.caption("An interactive plot of the 32 second segment that contains the GW190521 event.",help=graph_help())


st.subheader("What does this plot tell us?")

blurb4 = """
We have a trace of the Strain vs time for each of the three Interferometers. 

Looking at the entire 32 seconds it is quite hard to tell what is going on, but by zooming in 
(either using the button selector in the lower left of the plot, or by using the zoom tool), it becomes much more 
clear that there are distinct oscillating patterns occuring over the entire length of the data. There doesnt seem
to be any clear Gravitational Wave signal present in the data.

This is because the data s almost entirely dominated by noise. The Strain amplitude waves shown above have a period of around .10 seconds,
corresponding to ~10 Hz. This is likely caused by seismic activity on Earth picked up by interferometers as noise, not any 
astrophysical events (although there are GW mergers that occur in this frequency range).

We can see this more clearly if we look at the data in a new way. Instead of plotting Strain vs time, lets use a Fourier Transform 
and look at the Strain vs frequency. One common way of examining this relationship is the Amplitude Spectral Density (ASD). 

The ASD is a measure of the amount of amplitude present in the signal coming from certain frequency. As Gravitational Wave signals
caused by merging Black Holes are transient events (lasting only for a short time), most of the signal contains only noise.

"""
st.markdown(blurb4)

########################################################################################################

# PSD plot
PSD_data = load_PSD_data()
PSD_fig = create_new_figure()

ASD_data = load_ASD_data()


ASD_data = load_ASD_data()
ASD_fig = create_new_figure()

plot_freq_traces(ASD_fig,ASD_data,ifos=ifos)
apply_gw_freq_layout(ASD_fig,title = "Amplitude Spectral Density(ASD)", yrange = [-23.7,-19.9],ytitle="Strain/√Hz")

st.plotly_chart(ASD_fig, theme="streamlit",on_select="rerun",use_container_width=True)

st.caption("An interactive plot of the Amplitude Spectral Density for the GW190521 timeseries.",help=graph_help())

blurb5 = """
By looking at the ASD, we can clearly see spikes corresponding to high amounts of noise occurring at certain frequncies. 

As the figure is shown in logarithmic scale, it should also clear that the amount of noise is much greater at low frequncies. In fact, the the peak amplitude
for Ligo Livingston (occuring at roughly 10 Hz for all three detectors), corresponds to noise with an amplitude between 5000x and 36000x higher
than the region our GW signal is in. This makes it impossible to spot the GW signal without first taking steps to remove and correct for this unwanted noise.
"""
st.markdown(blurb5)
