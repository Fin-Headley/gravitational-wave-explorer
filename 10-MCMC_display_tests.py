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
#import plotly.express as px
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

st.set_page_config(page_title="MCMC result display testing", page_icon="📈",layout="wide")

st.title("lets plot some corners!")
st.write(
    "Lets look at how we can model GWs!"
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

#stacked = reduced_data.stack(sample=["chain", "draw"], inplace=False)

#Mass = stacked.posterior.Mass.values
#Ratio = stacked.posterior.Ratio.values
#Distance = stacked.posterior.Distance.values
#TimeShift = stacked.posterior.TimeShift.values
#Phase = stacked.posterior.Phase.values
#RA = stacked.posterior.RA.values
#Dec = stacked.posterior.Dec.values
#Incl = stacked.posterior.Incl.values
#Pol = stacked.posterior.Pol.values

mcmc_df = pd.read_parquet("mcmc_df_with_log_post.parquet")

def plot_hist(fig,x_data,plot_title,x_axis_title,nbins=50):
    fig.add_trace(go.Histogram(x=x_data,nbinsx=nbins),limit_to_view=True,max_n_samples = 60000)

    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        #hoversubplots="axis",
        width=500,
        height=500,
        title={
                    'text': plot_title,
                    'y': 0.9,
                    'x': .5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'automargin': True
                },

        yaxis=dict(
                title="Counts"),    #"Probability Density"),

        xaxis=dict(
            title=x_axis_title)

    )


columns = np.array(["Mass","Ratio","Distance","TimeShift","Phase","RA","Dec","Incl","Pol"])#"lp","chain","draw"])

columns_labels = np.array(["The Mass of the heavier object (Solar Masses)",
                           "Ratio of binary masses (Unitless)",
                           "The Luminosity distance to the GW event (Mega-Parsecs)",
                           "The detected time of the GW event",
                           "Coalesence phase of the binary (radians)",
                           "Right Ascension (Radians)",
                           "Declination (Radians)",
                           "Inclination angle (radians)",
                           "Polarization (Strain)"])#"lp","chain","draw"])


column_titles = np.array(["Mass","Ratio","Distance","TimeShift","Phase","Right Ascension","Declination","Inclination","Polarization"])

word_to_num_dict = {"Mass":0,"Ratio":1,"Distance":2,"TimeShift":3,"Phase":4,"Right Ascension":5,"Declination":6,"Inclination":7,"Polarization":8}


options = column_titles

col1, col2 = st.columns(2)

with col1:
    #st.header("Widget 1")
    top_column_picker = st.selectbox(
        "Select a value for Widget 1:",
        options,
        key="widget1_selector"  # Unique key for Widget 1
    )

#st.header("Widget 2")
# Filter options for Widget 2 based on the selection in Widget 1
# This ensures Widget 2 cannot select the same value as Widget 1
available_options_2 = [opt for opt in options if opt != top_column_picker]

# Set a default value for Widget 2 if the currently selected value in Widget 1
# is the only remaining option for Widget 2
if top_column_picker in options and len(available_options_2) == 0:
    default_index_2 = 0 if available_options_2 else None
elif top_column_picker in options and available_options_2:
    if st.session_state.get("widget2_selector") == top_column_picker:
        default_index_2 = available_options_2.index(available_options_2[0])
    else:
        try:
            default_index_2 = available_options_2.index(st.session_state.get("widget2_selector", available_options_2[0]))
        except ValueError:
            default_index_2 = 0
else:
    default_index_2 = 0

with col2:
    right_column_picker = st.selectbox(
        "Select a value for Widget 2(cannot be the same as Widget 1):",
        available_options_2,
        index=default_index_2,
        key="widget2_selector"  # Unique key for Widget 2
    )

#st.write(f"Value from Widget 1: {top_column_picker}")
#st.write(f"Value from Widget 2: {right_column_picker}")



top_column = word_to_num_dict[top_column_picker]
right_column = word_to_num_dict[right_column_picker]
#need to make decimals into two varibales and place them smartly


hist_df = mcmc_df[[columns[top_column], columns[right_column]]]


x_data = np.array(hist_df[columns[top_column]])
y_data = np.array(hist_df[columns[right_column]])

hist_data,xedges,yedges  = np.histogram2d(x_data,y_data,bins=[50,50])
hist_data = hist_data.T
#hist_data = np.flip(hist_data,0)

x_axis = hist_df[columns[top_column]]
y_axis = hist_df[columns[right_column]]
x_axis_label = columns_labels[top_column]
y_axis_label = columns_labels[right_column]

x_range = (np.min(x_data),np.max(x_data))
y_range = (np.min(y_data),np.max(y_data))

x_bin_list = list(xedges)
y_bin_list = list(yedges)

x_hist_data, trash = np.histogram(x_data,bins=x_bin_list)
y_hist_data, trash = np.histogram(y_data,bins=y_bin_list)




x_bin_ticks = np.round(xedges,decimals=3)
x_bin_ticks = x_bin_ticks.astype(str)
for i in range(len(x_bin_ticks)-1):
    x_bin_ticks[i] =  x_bin_ticks[i] + " - " + x_bin_ticks[i+1]
x_bin_ticks = x_bin_ticks[0:-1]

y_bin_ticks = np.round(yedges,decimals=3)
y_bin_ticks = y_bin_ticks.astype(str)
for i in range(len(y_bin_ticks)-1):
    y_bin_ticks[i] =  y_bin_ticks[i] + " - " + y_bin_ticks[i+1]
y_bin_ticks = y_bin_ticks[0:-1]


X_bin_var, Y_bin_var = np.meshgrid(x_bin_ticks,y_bin_ticks)

coordinates_array = np.stack((X_bin_var.ravel(), Y_bin_var.ravel()), axis=-1).reshape(Y_bin_var.shape[0], X_bin_var.shape[1], 2)

customdata = coordinates_array

x_bin_ticks_half_empty = x_bin_ticks.copy()
x_bin_ticks_half_empty[1::2] = ""

x_centers = 0.5 * (xedges[:-1] + xedges[1:])
y_centers = 0.5 * (yedges[:-1] + yedges[1:])


# Create heatmap
heatmap = go.Heatmap(
    x = x_centers,
    y = y_centers,
    z = hist_data,
    colorscale=px.colors.sequential.Viridis,    #Purples,gray_r
    colorbar=dict(title = "colorbar"),
    zmin = 0,
    #text=custom_text,
    #hovertext = list(x_bin_ticks),
    #hoverinfo="text",
    customdata = coordinates_array,
    hovertemplate='<b>'+column_titles[top_column]+' Bin</b>: %{customdata[0]}</br><b>'+column_titles[right_column]+' Bin</b>: %{customdata[1]}<br><b>Count</b>: %{z}<extra></extra>',
    #hovertemplate = '<br> %{x}'
    #hovertemplate= '<b>X Value</b>: %{x}<br><b>Y Value</b>: %{y:.2f}<br><i>Custom Info</i>: %{text}<extra></extra>',
    yaxis='y',
    xaxis='x',
)


x_hist = go.Bar(
    x = x_centers,
    y = x_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    customdata = x_bin_ticks,
    hovertemplate='<b>'+column_titles[top_column]+' Bin</b>: %{customdata}</br></br><b>Count</b>: %{y}<extra></extra>',
    showlegend=False,
    yaxis='y2',
)

y_hist = go.Bar(
    y = y_centers,
    x = y_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    customdata = y_bin_ticks,
    hovertemplate='<b>'+column_titles[right_column]+' Bin</b>: %{customdata}</br></br><b>Count</b>: %{x}<extra></extra>',
    showlegend=False,
    xaxis='x2',
    orientation='h',
)


# Build the figure layout
fig=go.Figure()

# Add traces
#fig.add_trace(Scatter_test)
fig.add_trace(heatmap)
fig.add_trace(x_hist)
fig.add_trace(y_hist)


xtick_vals = list(np.round(np.linspace(x_range[0],x_range[1],10),decimals=0))
xticktext = [str(i) for i in xtick_vals]



fig.update_layout(
    xaxis=dict(domain=[0, 0.85], 
               title=x_axis_label,
               tickmode = 'array',
               tickvals = xtick_vals,
               ticktext = xticktext,
               showticklabels=True
                ),
    yaxis=dict(domain=[0, 0.85], title=y_axis_label),
    xaxis2=dict(domain=[0.86, 1], showticklabels=False),
    yaxis2=dict(domain=[0.86, 1], showticklabels=False),
    title={'text': column_titles[top_column]+" vs "+column_titles[right_column],
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    hovermode='closest',
    bargap=0.05,
    width=700,
    height=700,
)


#fig_resampler = FigureResampler(fig)

# Set up layout with subplots manually


# Make the marginal histograms align properly
#fig.update_traces(
#    selector=dict(type='histogram'),
#    opacity=0.6
#)

# Adjust specific histograms’ orientation and axes
#fig.update_traces(
    #selector=dict(yaxis='y2'),
    #xbins=dict(size=(df["Mass"].max() - df["Mass"].min()) / 30)
#)
#fig.update_traces(
    #selector=dict(xaxis='x2'),
    #orientation='h',
    #ybins=dict(size=(df["Ratio"].max() - df["Ratio"].min()) / 30)
#)

st.plotly_chart(fig,use_container_width=False)

#corner_test = corner.corner(test_array)

#st.pyplot(corner_test)

#from arviz_plots import plot_dist, plot_forest, plot_trace_dist, style # pyright: ignore[reportMissingImports]
#import arviz_plots as azp

#mcmc_df = pd.read_parquet("reduced_mcmc_results.parquet")

#trace_test = az.plot_trace(reduced_data,var_names=["Incl"],circ_var_names=["Incl"],combined=True,show=True,backend = "bokeh")