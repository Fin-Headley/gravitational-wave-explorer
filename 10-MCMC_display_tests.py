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


mcmc_df = pd.read_parquet("reduced_mcmc_results.parquet")

def plot_hist(fig,x_data,plot_title,x_axis_title,nbins=50):
    fig.add_trace(go.Histogram(x=x_data,nbinsx=nbins,histnorm='probability density'),limit_to_view=True,max_n_samples = 60000)

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
                title="Probability Density"),

        xaxis=dict(
            title=x_axis_title)

    )

test_hist = create_new_figure()
plot_hist(test_hist,mcmc_df["Mass"],"Mass","Mass (Solar Mass)")

st.plotly_chart(test_hist, theme="streamlit",on_select="rerun",use_container_width=True)


import plotly.express as px
df = px.data.tips()

Mass_Ratio = mcmc_df[["Mass", "Ratio"]]

fig = px.density_heatmap(Mass_Ratio, x="Mass", y="Ratio", marginal_x="histogram", marginal_y="histogram")
fig.show()


#corner_test = corner.corner(test_array)

#st.pyplot(corner_test)

#from arviz_plots import plot_dist, plot_forest, plot_trace_dist, style # pyright: ignore[reportMissingImports]
#import arviz_plots as azp

#mcmc_df = pd.read_parquet("reduced_mcmc_results.parquet")

#trace_test = az.plot_trace(reduced_data,var_names=["Incl"],circ_var_names=["Incl"],combined=True,show=True,backend = "bokeh")