import streamlit as st
import numpy as np
from gwosc.datasets import event_gps
from astropy.time import Time
import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler import FigureResampler # type: ignore
from tools.plotly_templates import *
from tools.data_caching import *
from tools.gen_template_function import *
import pandas as pd
from plotly.subplots import make_subplots

st.set_page_config(page_title="results", page_icon="📈",layout="wide")

st.title("Results:")
st.write(
    "lets take a look at my best fitting parameters."
)
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
datetime_center = Time(time_center, format='gps').utc.datetime  # type: ignore

#ifos = ['L1','H1']
########################################################################

#burnin = 35426 
#thin = 2

MAP_df = pd.read_parquet("MCMC_data/MAP_parameters.parquet")
MAP_df.rename(inplace=True,index={"TimeShift":"Time Shift","RA":"Right Ascension","Dec":"Declination","Incl":"Inclination","Pol":"Polarization","lp":"Log Posterior","chain":"Chain","draw":"Draw"})

results_df = MAP_df.copy()

column_dec_value = {"Mass":1,"Ratio":2,"Distance":0,"Time Shift":5,"Phase":2,"Right Ascension":4,"Declination":3,"Inclination":2,"Polarization":3}

column_titles = np.array(["Mass","Ratio","Distance","Time Shift","Phase","Right Ascension","Declination","Inclination","Polarization"])


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


def get_results(index="Mass"):

    MAP=results_df["MAP"].loc[index]
    onesig_low,onesig_high = results_df["onestd"].loc[index]
    twosig_low, twosig_high = results_df["twostd"].loc[index]
    return MAP,onesig_low, onesig_high, twosig_low, twosig_high


st.write("Here are my Maximum a posteriori estimates for each of the model parameters, shown with 95% confidence values.")


results_col1, results_col2 = st.columns([1,1],gap=None)


with results_col1:
        
    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Mass")
    st.latex(rf"""M_1={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \;""",help="Primary Mass")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Ratio")
    st.latex(rf"""q={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Mass Ratio")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Distance")
    st.latex(rf"""D_L={int(MAP)}^{{{int(twosig_high)}}}_{{{int(twosig_low)}}} \; """,help="Luminosity Distance")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Phase")
    st.latex(rf"""\phi_c={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Coalesence Phase")

with results_col2:
    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Right Ascension")
    st.latex(rf"""\alpha={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Right Ascension")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Declination")
    st.latex(rf"""\delta={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Declination")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Inclination")
    st.latex(rf"""i={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Inclination")

    MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Polarization")
    st.latex(rf"""P={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Polarization")



MAP, onesig_low, onesig_high, twosig_low, twosig_high = get_results("Time Shift")
st.latex(rf"""TimeShift={MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; """,help="Time from event_gps('GW190521')")
#st.latex(rf"""TimeShift={MAP}^{{{onesig_high}}}_{{{onesig_low}}} \; (\text{{1$\sigma$}}),\quad{MAP}^{{{twosig_high}}}_{{{twosig_low}}} \; (\text{{2$\sigma$}})""")



st.subheader("Plotting a MAP parameter model against data")

MAP_params = []
for i in range(9):
    MAP_params.append(results_df["MAP"].iloc[i])


MAP_template = gen_template(MAP_params)

L1_white_template = MAP_template["L1"].whiten(asd=np.sqrt(PSD_data["L1"]),highpass=25.,lowpass = 90.)
H1_white_template = MAP_template["H1"].whiten(asd=np.sqrt(PSD_data["H1"]),highpass=25.,lowpass = 90.)
V1_white_template = MAP_template["V1"].whiten(asd=np.sqrt(PSD_data["V1"]),highpass=25.,lowpass = 90.)

colors = load_colours_dict()

tab1, tab2, tab3 = st.tabs(["Single Detector","Two Detectors","Three Detectors"])


with tab1:
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    apply_gw_1_model_comparision_layout(fig_resampler,title='MAP Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("Whitened MAP model compared to whitened Ligo Livingston strain data.",help=graph_help_no_buttons())


with tab2:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford MAP Model",row=2,col=1)

    apply_gw_2_model_comparision_layout(fig_resampler,title='MAP Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("Whitened MAP model compared to whitened Ligo strain data.",help=graph_help_no_buttons())


with tab3:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
    fig_resampler = FigureResampler(fig)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["L1"].value,colors["L1"],"Livingston",row=1,col=1)
    add_GW_trace_subplot(fig_resampler,L1_white_template.times.value,L1_white_template.value,"black","Livingston MAP Model",row=1,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["H1"].times.value,GW_data["H1"].value,colors["H1"],"Hanford",row=2,col=1)
    add_GW_trace_subplot(fig_resampler,H1_white_template.times.value,H1_white_template.value,"black","Hanford MAP Model",row=2,col=1)

    add_GW_trace_subplot(fig_resampler,GW_data["L1"].times.value,GW_data["V1"].value,colors["V1"],"Virgo",row=3,col=1)
    add_GW_trace_subplot(fig_resampler,V1_white_template.times.value,V1_white_template.value,"black","Virgo MAP Model",row=3,col=1)

    apply_gw_3_model_comparision_layout(fig_resampler,title='MAP Model vs Data')

    st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=True)
    st.caption("Whitened MAP model compared to whitened Ligo/Virgo strain data.",help=graph_help_no_buttons())


################################################################################################################################################

st.header("Signal to Noise Ratio")

SNRs = {}
SNR_Peaks = {}

ifos = ['L1','H1','V1']
colours = load_colours_dict()

labels = load_labels_dict()

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

    SNR_Peaks[ifo] = round(SNRmax,3)
    #st.write('Maximum {} SNR of {} at {}.'.format(ifo,SNRmax,time_max))


st.markdown(
r"""
Below are the Signal to Noise Ratios for each of the detectors, using the MAP model as the signal.
""")


st.write(":blue-background[Ligo-Livingston] had a Peak Signal to Noise Ratio of :blue[{}].".format(SNR_Peaks["L1"]))

st.write(":red-background[Ligo-Hanford] had a Peak Signal to Noise Ratio of :red[{}].".format(SNR_Peaks["H1"]))

st.write(":violet-background[Virgo] had a Peak Signal to Noise Ratio of :violet[{}].".format(SNR_Peaks["V1"]))


fig = make_subplots(rows=1, cols=3, shared_xaxes="all",shared_yaxes="all",horizontal_spacing=.03 ,vertical_spacing=0.05,) # type: ignore

fig_resampler = FigureResampler(fig)

add_GW_trace_subplot(fig_resampler,SNRs["L1"].times.value,SNRs["L1"].value,colours["L1"],labels["L1"],row=1,col=1)
add_GW_trace_subplot(fig_resampler,SNRs["H1"].times.value,SNRs["H1"].value,colours["H1"],labels["H1"],row=1,col=2)
add_GW_trace_subplot(fig_resampler,SNRs["V1"].times.value,SNRs["V1"].value,colours["V1"],labels["V1"],row=1,col=3)


Apply_SNR_layout(fig_resampler,"Detector Signal to Noise Ratios")

st.plotly_chart(fig_resampler, theme="streamlit",on_select="rerun",use_container_width=False)
st.caption("The Signal to Noise Ratio of the MAP parameter model with each Detector's Strain data.",help=graph_help_no_buttons())

st.divider()
################################################################################################################################################

st.header("Time-Frequency Spectrograms")

st.markdown(
r"""
Instead of looking at the data in the time domain or the frequency domain, a Spectrogram represents both. A spectrogram represents a signal's power per frequency, over a period of time.

To convert the (whitened) Strain data into a Spectrogram we use something called a Q-transform, which takes timeseries data and creates high-resolution time-frequency maps. 
If scaled properly, Q-transform provide a great visual reference of Gravitational Wave signals.

Additionally, we can use Q-transforms to preform one last test of the MAP model. We subtract the MAP model wave from the Strain data, and then Q-transform the subtracted timeseries. 
The resulting Spectrogram shows how well the model captured the GW event, as it should hopefully showcase uniform background noise.
""")


best_fit_template = gen_template(MAP_params)
data = load_raw_data()

data_qspecgram = {}

subtracted_qspecgram = {}


for ifo in ifos:
    subtracted = data[ifo] - best_fit_template[ifo]

    data_qspecgram[ifo]=data[ifo].whiten(asd=np.sqrt(PSD_data[ifo])).q_transform(outseg=(time_center - .5, time_center + .5),frange=(15, 150))
    subtracted_qspecgram[ifo]=subtracted.whiten(asd=np.sqrt(PSD_data[ifo])).q_transform(outseg=(time_center - .5, time_center + .5),frange=(15, 150))

data_times = load_raw_data()
data_times["L1"].crop(gps-.5,gps+.5)
times = data_times["L1"].times.value
t = Time(times, format='gps')         
x_datetime = t.utc.datetime    # type: ignore


def add_qtransform_subplot(fig,qspecgram,ifo='L1',showscale = False,colorbar=dict(title = "colorbar"),row=1,col=1):
    data_times = load_raw_data()
    data_times["L1"].crop(gps-.5,gps+.5)
    times = data_times["L1"].times.value
    t = Time(times, format='gps')        
    x_datetime = t.utc.datetime    # type: ignore

    zvar=0
    if ifo=='L1':
        zvar=150
    elif ifo=='H1':
        zvar=90
    elif ifo=='V1':
        zvar=60

    fig.add_trace(go.Heatmap(
        x = x_datetime,
        y0 = 15,
        dy=(150-15)/len((qspecgram[ifo][0])),
        z = qspecgram[ifo].T,
        zmin = 0,
        zmax = zvar,
        colorscale=px.colors.sequential.Viridis,    #Purples,gray_r
        colorbar=colorbar,
        showscale = showscale,
        #zmin = 0,
        #customdata = coordinate_array,
        hovertemplate='<b>Time</b>: %{x}</br><b>Frequency</b>: %{y} Hz<br><b>Normalized Energy</b>: %{z}<extra></extra>',
        #yaxis='y',
        #xaxis='x',
        ),
        row=row,
        col=col,
    )

Q_fig = make_subplots(rows=3, cols=2, shared_xaxes="all", horizontal_spacing=.03 ,vertical_spacing=0.05,shared_yaxes="all")# type: ignore #column_titles=[labels["L1"]+" SNR",labels["H1"]+" SNR",labels["V1"]+" SNR"])

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='L1',row=1,col=1,showscale=True,colorbar=dict(title="Livingston", len=0.33, y=0.70,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='L1',row=1,col=2)

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='H1',row=2,col=1,showscale=True,colorbar=dict(title="Hanford", len=0.33, y=0.35,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='H1',row=2,col=2)

add_qtransform_subplot(Q_fig,data_qspecgram,ifo='V1',row=3,col=1,showscale=True,colorbar=dict(title="Virgo", len=0.33, y=0,yanchor="bottom"))
add_qtransform_subplot(Q_fig,subtracted_qspecgram,ifo='V1',row=3,col=2)

Q_fig.update_layout(
    width=800,
    height=900,

    title={
        'text': "Frequency Spectrogram Plots",
        'y': .98,
        'x': .5,
        'xanchor': 'center',
        'yanchor': 'top',
        #'automargin': True
    },

    xaxis=dict(
    title="Strain Spectrogram",
    side='top',

    ),

    xaxis2=dict(
    title="Model Subtracted Spectrogram",
    side='top',

    ),

    xaxis5=dict(
    type="date",
    showgrid=True,
    title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}",
    ),

    xaxis6=dict(
    type="date",
    showgrid=True,
    title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}"
    ),

    yaxis=dict(
    title="Frequency (Hz)",
    side='left',
    ),

    yaxis3=dict(
    title="Frequency (Hz)",
    side='left',
    ),

    yaxis5=dict(
    title="Frequency (Hz)",
    side='left',
    ),
)


st.plotly_chart(Q_fig,use_container_width=True)
st.caption("""
           Left: Time-Frequency Spectrograms of whitened Strain for each of the three Detectors. (Top to bottom: Livinston, Hanford, Virgo)   
           Right: Time-Frequency Spectrograms of whitened Strain with the MAP model Subtracted. Normalized to same scale as left-side plots.
           """,help=graph_help_no_buttons())


st.markdown(
"""
The clear yellow hotspots seen in the the two Ligo Spectrograms are the detected Gravitational Wave.
 The absense of yellow hotspots and the absense of any patterns in the background of the right hand 
 plots is a good indication that the MAP model is correctly approximating the Gravitational Wave signal, 
 but this does not mean that the MAP parameters accurately describe the source event.

 The absence of a clear yellow spot for the Virgo interferometer, even when normalized to a lower energy, confirms 
 that Virgo did not capture a clear signal from the GW190521 event. As the MCMC samplier ran without comparing to 
 the Vigro interferometer, this did not have any effect on the MAP parameters.  Having said that, the fact
 that both Virgo Spectrograms look identical is once again a good indication that the MAP model is a sensible 
 approximation, as it didn't incorrectly remove background noise from the Virgo Spectrogram.
""")
