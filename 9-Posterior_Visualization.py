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

st.set_page_config(page_title="Posterior_Visualization", page_icon="📈",layout="wide")

st.title("Posterior Sample parameters")

#pure_data = import_pure_data()
#raw_data = import_raw_data()
#bandpass_data = create_bandpass_data()
#whitend_data = create_whitend_data()
#GW_data = import_GW_data()

#PSD_data = import_PSD_data()

#code
#gets the time of the event and prints it
gps = event_gps('GW190521')
time_center = gps
datetime_center = Time(time_center, format='gps').utc.datetime # type: ignore

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

mcmc_df.rename(inplace=True,columns={"TimeShift":"Time Shift","RA":"Right Ascension","Dec":"Declination","Incl":"Inclination","Pol":"Polarization","lp":"Log Posterior","chain":"Chain","draw":"Draw"})


column_titles = np.array(["Mass","Ratio","Distance","Time Shift","Phase","Right Ascension","Declination","Inclination","Polarization"])
options = column_titles

col1, col2 = st.columns([3,1],gap=None)

with col2:
    st.header("Parameter Selection")
    top_column_picker = st.selectbox(
        "Select a parameter for the x axis:",
        options,
        key="widget1_selector"  # Unique key for Widget 1
    )

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

    right_column_picker = st.selectbox(
        "Select a **different** parameter for the y axis:",
        available_options_2,
        index=default_index_2,
        key="widget2_selector"  # Unique key for Widget 2
    )


columns_labels={"Mass": "The Mass of the heavier object (Solar Masses)",
                "Ratio":    "Ratio of Masses (Unitless)",
                "Distance": "The Luminosity distance to the GW event (Mega-Parsecs)",
                "Time Shift":    "The time shift from 3:02:29.4 (Seconds)",
                "Phase":    "Coalesence phase of the binary (Radians)",
                "Right Ascension":  "Right Ascension (Radians)",
                "Declination":  "Declination (Radians)",
                "Inclination":  "Inclination angle (Radians)",
                "Polarization": "Polarization (Strain)"}

column_dec_value = {"Mass":0,"Ratio":2,"Distance":0,"Time Shift":5,"Phase":2,"Right Ascension":2,"Declination":3,"Inclination":2,"Polarization":2}



#def make_corner_plot(df = mcmc_df,top_column_picker = top_column_picker,right_column_picker=right_column_picker,columns_labels=columns_labels,column_dec_value=column_dec_value):

x_data = np.array(mcmc_df[top_column_picker])
y_data = np.array(mcmc_df[right_column_picker])

hist_data,xedges,yedges  = np.histogram2d(x_data,y_data,bins=[50,50])
hist_data = hist_data.T
#hist_data = np.flip(hist_data,0)

x_hist_data, trash = np.histogram(x_data,bins=list(xedges))
y_hist_data, trash = np.histogram(y_data,bins=list(yedges))
del trash


x_bin_ticks = np.round(xedges,decimals=column_dec_value[top_column_picker])
x_bin_ticks = x_bin_ticks.astype(str)
for i in range(len(x_bin_ticks)-1):
    x_bin_ticks[i] =  x_bin_ticks[i] + " - " + x_bin_ticks[i+1]
x_bin_ticks = x_bin_ticks[0:-1]

y_bin_ticks = np.round(yedges,decimals=column_dec_value[right_column_picker]) # type: ignore
y_bin_ticks = y_bin_ticks.astype(str)
for i in range(len(y_bin_ticks)-1):
    y_bin_ticks[i] =  y_bin_ticks[i] + " - " + y_bin_ticks[i+1]
y_bin_ticks = y_bin_ticks[0:-1]


X_bin_var, Y_bin_var = np.meshgrid(x_bin_ticks,y_bin_ticks)
coordinate_array = np.stack((X_bin_var.ravel(), Y_bin_var.ravel()), axis=-1).reshape(Y_bin_var.shape[0], X_bin_var.shape[1], 2) #coordinate array for hover labels

x_centers = 0.5 * (xedges[:-1] + xedges[1:]) #x axis markers for ticks
y_centers = 0.5 * (yedges[:-1] + yedges[1:]) #y axis markers for ticks


# Create heatmap

heatmap = go.Heatmap(
    x = x_centers,
    y = y_centers,
    z = hist_data,
    colorscale=px.colors.sequential.Viridis,    #Purples,gray_r
    colorbar=dict(title = "colorbar"),
    zmin = 0,
    customdata = coordinate_array,
    hovertemplate='<b>'+top_column_picker+' Bin</b>: %{customdata[0]}</br><b>'+right_column_picker+' Bin</b>: %{customdata[1]}<br><b>Count</b>: %{z}<extra></extra>',
    yaxis='y',
    xaxis='x',
)

x_hist = go.Bar(
    x = x_centers,
    y = x_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    customdata = x_bin_ticks,
    hovertemplate='<b>'+top_column_picker+' Bin</b>: %{customdata}</br></br><b>Count</b>: %{y}<extra></extra>',
    showlegend=False,
    yaxis='y2',
)

y_hist = go.Bar(
    y = y_centers,
    x = y_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    customdata = y_bin_ticks,
    hovertemplate='<b>'+right_column_picker+' Bin</b>: %{customdata}</br></br><b>Count</b>: %{x}<extra></extra>', # type: ignore
    showlegend=False,
    xaxis='x2',
    orientation='h',
)

fig=go.Figure()

fig.add_trace(heatmap)
fig.add_trace(x_hist)
fig.add_trace(y_hist)

fig.update_layout(
    xaxis=dict(domain=[0, 0.85], 
            title=columns_labels[top_column_picker],
            showticklabels=True
                ),
    yaxis=dict(domain=[0, 0.85], title=columns_labels[right_column_picker]), # type: ignore
    xaxis2=dict(domain=[0.86, 1], showticklabels=False),
    yaxis2=dict(domain=[0.86, 1], showticklabels=False),
    title={'text': top_column_picker+" vs "+right_column_picker,
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    hovermode='closest',
    bargap=0.05,
    width=600,
    height=600,
)



heatmap_help = """
Click on the dropdowns on the side to choose two parameters.
Click and drag on the plot to zoom in.
Double-click to reset axis to full graph.
"""

with col1:
    st.plotly_chart(fig,use_container_width=False)
    st.caption("A 2D heatmap showing the relationship between parameter posterior distributions, colored by count.",help=heatmap_help)


st.markdown(
r"""
Above is the MCMC sample of 774,888 parameter combinations mentioned in the :blue-background[Statistical Sampling] tab.

Two parameters are plotted at at time, one on the x-axis and one on the y-axis.

The histograms along the axes plot the 1D posterior distribution for the parameter, 
while the heatmap shows the 2D parameter space.

The MCMC MAP parameters, along with their uncertainties, are given in the :blue-background[Results] tab.
""")
