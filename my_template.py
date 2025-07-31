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
from plotly_resampler import FigureResampler
from datetime import timedelta


import plotly.graph_objects as go
import plotly.io as pio

gps = event_gps('GW190521')

segment = ((gps)-16, (gps)+16)

time_center = gps
datetime_center = Time(time_center, format='gps').utc.datetime


data = {}

ifos = ['L1', 'V1', 'H1']

for ifo in ifos:
    filename = f"GW190521_data/{ifo}_data_32s.hdf5"
    data[ifo] = TimeSeries.read(filename)

    times = data[ifo].times.value          # array of GPS seconds
    t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime

    t0 =x_datetime[0]


pio.templates["my_custom_template"] = go.layout.Template(
    # LAYOUT
    layout = {
        "title":{
            'text':'Observed GW Strain Data',
            'y':0.9,
            'x':.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin' : True},

        'hovermode': 'x unified',

        "yaxis" : {
            "title" : "Strain",
            "fixedrange" : False,
            "showexponent" : "all",
            "exponentformat" : "power",
            "nticks":5,
            "hoverformat" : ".3e",
            },
        
        "xaxis":dict(
            rangeslider=dict(visible=True),
            title = "Time (seconds) since "+str(t0).format("fits"),
            type="date",
            nticks=15,
            showgrid=True,
            hoverformat = "Time: %H:%M:%S.%3f",
        ),

        "legend":dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1
        ),

        "updatemenus":[dict(
                    type="dropdown",
                    direction="up",
                    active=5,
                    x=0,y=0, xanchor="left", yanchor="bottom", 
                    pad={"r": -10, "t": 0, "b": 0, "l": 0},#around outside of button
                    font ={"size" : 12},
                    showactive = True,
                    buttons=[
                        dict(label="±0.1 s", method="relayout",
                            args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.1),datetime_center+timedelta(seconds=.1)]}]),
                        dict(label="±0.2 s", method="relayout",
                            args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.2),datetime_center+timedelta(seconds=.2)]}]),
                        dict(label="±.5 s", method="relayout",
                            args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.5),datetime_center+timedelta(seconds=.5)]}]),
                        dict(label="±1 s", method="relayout",
                            args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=1),datetime_center+timedelta(seconds=1)]}]),
                        dict(label="±2 s", method="relayout",
                            args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=2),datetime_center+timedelta(seconds=2)]}]),
                        dict(label="Full", method="relayout",
                            args=[{"yaxis.autorange": True,"xaxis.autorange": True } ])
                    ]
                ),
                ],

    },

    # DATA
    data = {
        # Each graph object must be in a tuple or list for each trace
        'bar': [go.Bar(texttemplate = '%{value:$.2s}',
                       textposition='outside',
                       textfont={'family': 'Helvetica Neue, Helvetica, Sans-serif',
                                 'size': 20,
                                 'color': '#FFFFFF'
                                 })]
    }
)