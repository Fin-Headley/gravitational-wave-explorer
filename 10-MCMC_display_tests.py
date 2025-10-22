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
reduced_data = az.from_netcdf("MCMC_processed_data.nc")

stacked = reduced_data.stack(sample=["chain", "draw"], inplace=False)

Mass = stacked.posterior.Mass.values
Ratio = stacked.posterior.Ratio.values
Distance = stacked.posterior.Distance.values
TimeShift = stacked.posterior.TimeShift.values
Phase = stacked.posterior.Phase.values
RA = stacked.posterior.RA.values
Dec = stacked.posterior.Dec.values
Incl = stacked.posterior.Incl.values
Pol = stacked.posterior.Pol.values

#test_array = {}
#test_array["Mass"] = Mass
#test_array["Ratio"] = Ratio
#est_array["Distance"] = Distance
#test_array

#fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,shared_yaxes=True)
#fig_resampler = FigureResampler(fig)


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

#test_hist = create_new_figure()
#plot_hist(test_hist,mcmc_df["Mass"],"Mass","Mass (Solar Mass)")

#st.plotly_chart(test_hist, theme="streamlit",on_select="rerun",use_container_width=True)

import nbformat
#st.write(nbformat.__version__)
import plotly.express as px


#st.write(mcmc_df)

#fig2 = px.density_heatmap(Mass_Ratio, x="Mass", y="Ratio", marginal_x="histogram", marginal_y="histogram",color_continuous_scale=px.colors.sequential.Viridis)
#fig.update_layout(marker=dict(opacity=0.1))

#st.plotly_chart(fig2)

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


hist_df = mcmc_df[[columns[0], columns[1]]]


x_data = np.array(hist_df["Mass"])
y_data = np.array(hist_df["Ratio"])

hist_data,xedges,yedges  = np.histogram2d(x_data,y_data,bins=[50,50])
hist_data = hist_data.T
#hist_data = np.flip(hist_data,0)

x_axis = hist_df[columns[0]]
y_axis = hist_df[columns[1]]
x_axis_label = columns_labels[0]
y_axis_label = columns_labels[1]

x_bin_list = list(xedges)
y_bin_list = list(yedges)

x_hist_data, trash = np.histogram(x_data,bins=x_bin_list)
y_hist_data, trash = np.histogram(y_data,bins=y_bin_list)

def colorbar(zmin, zmax, n = 6):
    return dict(
        title = "Log color scale",
        tickmode = "array",
        tickvals = np.linspace(np.log10(zmin), np.log10(zmax), n),
        ticktext = np.round(10 ** np.linspace(np.log10(zmin), np.log10(zmax), n), 1)
    )

zmin = 1
zmax = 12000

import math
#math.log(number, base)

# Create 2D histogram for density heatmap
heatmap = go.Heatmap(
    #x=x_axis,
    #y=y_axis,
    #z = np.log(hist_data+.1),
    #np.log2(hist_data+.1),
    z = hist_data,
    colorscale=px.colors.sequential.Purples,    #Purples,gray_r
    colorbar=dict(title = "colorbar"),
    #nbinsx=50,
    #nbinsy=50,
    #zauto = True,
    #zmid = 10,
    zmin = 0,
    #zmax = 7000,
)


"""heatmap = go.Histogram2d(
    x=x_axis,
    y=y_axis,
    colorscale=px.colors.sequential.Purples,    #Purples,gray_r
    colorbar=dict(title = "colorbar"),
    nbinsx=50,
    nbinsy=50,
    #zauto = True,
    #zmid = 4000,
    #zmin = 0,
    #zmax = 10000,
)"""
"""
Scatter_test = (go.Scatter(
        x = x_axis,
        y = y_axis,
        xaxis = 'x',
        yaxis = 'y',
        mode = 'markers',
        marker = dict(
            color = 'rgba(0,0,0,0.3)',
            size = 3
        )
    ))
"""

# Create marginal histograms
"""x_hist = go.Histogram(
    x=x_axis,
    nbinsx=50,
    marker_color=px.colors.sequential.Purples[-1],
    showlegend=False,
    yaxis='y2',
    #ybins=50,
)"""

x_hist = go.Bar(
    x=np.arange(0,50,1),
    y = x_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    showlegend=False,
    yaxis='y2',
    #ybins=50,
)

y_hist = go.Bar(
    y = np.arange(0,50,1),
    x = y_hist_data,
    marker_color=px.colors.sequential.Purples[-1],
    showlegend=False,
    xaxis='x2',
    #xbins=50,
    orientation='h'
)


# Build the figure layout
fig=go.Figure()

# Add traces
#fig.add_trace(Scatter_test)
fig.add_trace(heatmap)
fig.add_trace(x_hist)
fig.add_trace(y_hist)

fig.update_layout(
    xaxis=dict(domain=[0, 0.85], title=x_axis_label),
    yaxis=dict(domain=[0, 0.85], title=y_axis_label),
    xaxis2=dict(domain=[0.86, 1], showticklabels=False),
    yaxis2=dict(domain=[0.86, 1], showticklabels=False),
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


st.plotly_chart(fig)

#corner_test = corner.corner(test_array)

#st.pyplot(corner_test)

#from arviz_plots import plot_dist, plot_forest, plot_trace_dist, style # pyright: ignore[reportMissingImports]
#import arviz_plots as azp

#mcmc_df = pd.read_parquet("reduced_mcmc_results.parquet")

#trace_test = az.plot_trace(reduced_data,var_names=["Incl"],circ_var_names=["Incl"],combined=True,show=True,backend = "bokeh")