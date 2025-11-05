"""
Plotly layout templates and helper functions for displaying GW strain data on streamlit
"""
import streamlit as st
from datetime import timedelta
from astropy.time import Time
from plotly_resampler import FigureResampler # type: ignore
from tools.data_caching import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def graph_help():
    """
    Returns standard text for a help pop-up for a plot.
    """
    output_text = """Use the button in the lower right to view preset ranges.   
                    You can hide/show GW Observatories by clicking on their name in the legend.  
                    Click to pan.    
                    Change tools in the top right to use custom zooms.   
                    Double-click to reset axis to full graph."""
    return output_text

def graph_help_no_buttons():
    """
    Returns standard text for a help pop-up for a plot with no zoom buttons.
    """
    output_text = """You can hide/show GW Observatories by clicking on their name in the legend.  
                    Click to pan.    
                    Change tools in the top right to use custom zooms.   
                    Double-click to reset axis to full graph."""
    return output_text


def apply_gw_strain_layout(fig, title = "needs a title", datetime_center = Time(1242442967.444, format='gps').utc.datetime, data_range = "pure"): # type: ignore
    """
    Apply a standardized layout template for gravitational wave strain data plots.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    datetime_center : datetime, optional
        Center time for the plot and zoom controls (default: slightly shifted GW190521 event time)
    data_range : str, optional
        Data type for appropriate y axis scaling: 'pure', 'raw', 'bandpass', 
        'whiten', 'GW_data', or 'example_model' (default: 'pure')
        
    Notes
    -----
    The function adds:
    - Interactive dropdown menu for time ranges (±0.1s to ±16s)
    - Data-type-specific y-axis scaling and labels
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Horizontal legend positioned at top-right
    
    Y-axis labels and scale automatically adjust between "Strain Amplitude" for raw data
    and "Normalized Strain Amplitude" for processed data (whitened/GW_data).
    """
                                #±0.1 y range,  #±0.2 y range, #±0.5 y range,#±1 y range
    data_range_dict = {"pure":[[-2.4e-19,2.4e-19],[-4e-19,4e-19],[-7e-19,7e-19],[-9e-19,9e-19]], 
                        "raw":[[-2.4e-19,2.4e-19],[-4e-19,4e-19],[-7e-19,7e-19],[-9e-19,9e-19]],
                        "bandpass":[[-8.1e-22,8.1e-22],[-8.1e-22,8.1e-22],[-8.1e-22,8.1e-22],[-8.1e-22,8.1e-22]],
                        "whiten":[[-4,4],[-4,4],[-4,4],[-4,4]],                       
                        "GW_data": [[-1.2,1.2],[-1.2,1.2],[-1.2,1.2],[-1.2,1.2]],
                        "example_model":[[-3.1e-22,3.1e-22],[-3.1e-22,3.1e-22],[-3.1e-22,3.1e-22],[-3.1e-22,3.1e-22]],
                        }

    full_button_name = "± 2 s"
    if data_range == "pure":
        full_button_name = "± 16 s"


    if data_range == "whiten":
        y_title = "Normalized Strain Amplitude"
    elif data_range == "GW_data":
        y_title = "Normalized Strain Amplitude"
    else:
        y_title = "Strain Amplitude"

    y_range_list = data_range_dict[data_range]


    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        #hoversubplots="axis",
        width=700,
        height=500,

        # X range dropdown menu
        updatemenus=[dict(
            type="dropdown",
            direction="up",
            active=4,
            x=.03, y=0, 
            xanchor="left", 
            yanchor="bottom", 
            pad={"r": -10, "t": 0, "b": 0, "l": 0},  # padding around outside of button
            font={"size": 12},
            showactive=True,
            buttons=[
                dict(label="±0.1 s", method="relayout",
                    args=[{
                        "xaxis.autorange": False, 
                        "xaxis.range": [datetime_center-timedelta(seconds=.1), datetime_center+timedelta(seconds=.1)],
                        "yaxis.range": y_range_list[0]
                        }]),
                dict(label="±0.2 s", method="relayout",
                    args=[{"xaxis.autorange": False, 
                           "xaxis.range": [datetime_center-timedelta(seconds=.2), datetime_center+timedelta(seconds=.2)],
                           "yaxis.range": y_range_list[1]
                           }]),
                dict(label="±.5 s", method="relayout",
                    args=[{"xaxis.autorange": False, 
                           "xaxis.range": [datetime_center-timedelta(seconds=.5), datetime_center+timedelta(seconds=.5)],
                           "yaxis.range": y_range_list[2]
                           }]),
                dict(label="±1 s", method="relayout",
                    args=[{"xaxis.autorange": False, 
                           "xaxis.range": [datetime_center-timedelta(seconds=1), datetime_center+timedelta(seconds=1)],
                            "yaxis.range": y_range_list[3]
                           }]),
                dict(label=full_button_name, method="relayout",
                    args=[{"yaxis.autorange": True, "xaxis.autorange": True}])
            ]
        )],
        
        # Title settings
        title={
            'text': title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },
        
        # Y-axis settings
        yaxis=dict(
            title=y_title, #dict(text=y_title,standoff=0),
            fixedrange=False,
            #showexponent="all",
            exponentformat="e",
            #nticks=5,
            #tickangle = -30,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),

        # X-axis settings
        xaxis=dict(
            #rangeslider=dict(visible=True),
            title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', mirror=True, showline=True,
            domain=[.03, 0.97]
        ),
        
        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=.97,
            borderwidth=1, bordercolor='black',
        ),
    )
    fig.update_yaxes(showline=True, mirror=True, linecolor="black", linewidth=1) #backup to get outside lines to show



def add_freq_event_shading(fig, freq_start, freq_end, fillcolor="chartreuse",opacity=0.25,line_width=0):
    """
    Add a frequency band shading region to a plot.
    
    Creates a vertical rectangular shaded region between two frequency values.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to add the shading to
    freq_start : float
        Starting frequency of the shaded region in Hz
    freq_end : float
        Ending frequency of the shaded region in Hz
    fillcolor : str, optional
        Color of the shaded region (default: "chartreuse")
    opacity : float, optional
        Transparency of the shaded region, range 0-1 (default: 0.25)
    line_width : int, optional
        Width of the border line around the shaded region (default: 0)
        
    """
    fig.add_vrect(x0=freq_start
                  ,x1=freq_end
                  ,fillcolor=fillcolor
                  ,opacity=opacity
                  ,line_width=line_width)


def create_new_figure():
    """
    Create a new FigureResampler figure optimized for online data visualization.
    
    Returns a FigureResampler object configured with settings optimized for 
    displaying large datasets with high accuracy over a wide range of domains.
    
    Returns
    -------
    plotly_resampler.FigureResampler
        A FigureResampler object that traces can be added to.
        
    Notes
    -----
    FigureResampler is used instead of standard Plotly figures to handle
    the large time series datasets present in these datasets. The resampling 
    maintains correct features while providing smooth interactive performance.
    """
    return FigureResampler(resampled_trace_prefix_suffix = ("",""), default_n_shown_samples = 1000, show_mean_aggregation_size= False, create_overview=True)


def plot_traces(fig,data_dictionary,ifos,alpha={"L1":1,"H1":1,"V1":1}):
    """
    Add gravitational wave strain data traces to a plotly figure.
    
    Adds time series traces for specified interferometers to a timeseries 
    Plotly figure with datetime format. Uses standard GW detector colors 
    and labels with resampling for web performance.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to add traces to
    data_dictionary : dict
        Dictionary containing TimeSeries data with interferometer keys 
    ifos : list of str
        List of interferometer keys to plot (e.g., ['L1', 'H1', 'V1'])
    alpha : dict, optional
        Dictionary mapping interferometer codes to opacity values (0-1).
        Default: {"L1":1, "H1":1, "V1":1}
        
    Notes
    -----
    The function automatically:
    - Converts GPS times to UTC datetime objects for proper x-axis display
    - Applies standard detector colors
    - Uses short detector labels (Hanford, Livingston, Virgo)
    - Limits display to 60,000 samples for optimal performance
    - Enables view-based resampling when using FigureResampler
    
    Time series data is expected to be GWpy TimeSeries objects.
    """
    colours = load_colours_dict()
    short_labels = load_short_labels_dict()

    for ifo in ifos:

        times = data_dictionary[ifo].times.value     # array of GPS seconds
        t = Time(times, format='gps')                # make an Astropy Time array (GPS scale)
        x_datetime = t.utc.datetime # type: ignore   # numpy array of Python datetimes
                                        
        fig.add_trace(go.Scatter(                    #plotly.go.Figure args
            mode='lines',
            line_color=colours[ifo],
            showlegend=True,
            name=short_labels[ifo],
            opacity= alpha[ifo]
        
        ),
        hf_x = x_datetime,                           #plotly_resampler.FigureResampler args
        hf_y = data_dictionary[ifo].value,
        limit_to_view=True,
        max_n_samples = 60000                        #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )


def plot_single_trace(fig,data_dictionary,ifo="L1"):
    """
    Add single gravitational wave strain data trace to a plotly figure.
    
    Adds time series trace for specified interferometer to a timeseries 
    Plotly figure with datetime format. Uses standard GW detector color 
    and label with resampling for web performance.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to add trace to
    data_dictionary : dict
        Dictionary containing TimeSeries data with interferometer keys 
    ifo : str
        Interferometer key used to plot trace (default: "L1")
        
    Notes
    -----
    The function automatically:
    - Converts GPS times to UTC datetime objects for proper x-axis display
    - Applies standard detector color
    - Uses short detector label (Hanford, Livingston, Virgo)
    - Limits display to 60,000 samples for optimal performance
    - Enables view-based resampling when using FigureResampler
    
    Time series data is expected to be GWpy TimeSeries objects.
    """
    colours = load_colours_dict()
    short_labels = load_short_labels_dict()

    times = data_dictionary.times.value             # array of GPS seconds
    t = Time(times, format='gps')                   # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime # type: ignore      # numpy array of Python datetimes
                                    
    fig.add_trace(go.Scatter(                       #plotly.go.Figure args
        mode='lines',
        line_color=colours[ifo],
        showlegend=True,
        name=short_labels[ifo],
    
    ),
    hf_x = x_datetime,                               #FigureResampler args
    hf_y = data_dictionary.value,
    limit_to_view=True,
    max_n_samples = 60000                            #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )


def plot_freq_traces(fig,data_dictionary,ifos = ['L1', 'V1', 'H1']):
    """
    Add gravitational wave strain data traces to a plotly figure.
    
    Adds frequency series traces for specified interferometers to a Plotly 
    figure. Uses standard GW detector colors and labels with resampling 
    for web performance.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to add traces to
    data_dictionary : dict
        Dictionary containing FrequencySeries data with interferometer keys 
    ifos : list of str
        List of interferometer keys to plot (e.g., ['L1', 'H1', 'V1'])
        
    Notes
    -----
    The function automatically:
    - Applies standard detector colors
    - Uses short detector labels (Hanford, Livingston, Virgo)
    - Limits display to 100,000 samples for optimal performance
    - Enables view-based resampling when using FigureResampler
    
    Time series data is expected to be GWpy TimeSeries objects.
    """
    colours = load_colours_dict()
    short_labels = load_short_labels_dict()

    for ifo in ifos:
        fig.add_trace(go.Scatter(
            mode='lines',
            line_color=colours[ifo],
            showlegend=True,
            name=short_labels[ifo],
        
        ),
        hf_x = data_dictionary[ifo].frequencies,
        hf_y = data_dictionary[ifo].value,
        limit_to_view=True,
        max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )


def apply_gw_freq_layout(fig, title = "needs a title", yrange = [-23.7,-19.9],xrange =[1,3],ytitle="Strain Noise [1/HZ]"):
    """
    Apply a standardized layout template for gravitational wave strain frequency data plots.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    yrange : list[float, float], optional
        Log range for y-axis as [minimum, maximum] values.
        Given for log scale plot, actual plot y-range will be [1*10^minimum,1*10^maximum] 
        (default: [-23.7,-19.9]) -> actual range [10^-23.7,10^-19.9]
    xrange : list[float, float], optional
        Log range x-axis for zoomed plot as [minimum, maximum] values.
        Given for log scale plot, actual plot x-range will be [1*10^minimum,1*10^maximum] 
        (default: [1,3]) -> actual range [10,1000] (Hz)
    ytitle : str, optional
        Title for the y-axis of the plot (default: "Strain Noise [1/HZ]")
        
    Notes
    -----
    This function adds:
    - Interactive dropdown menu for frequency ranges (Full:[.25,2048]Hz, Zoomed:[10,1000]Hz, Bandpass:[25,90]Hz)
    - Data-specific y-axis scaling and labels
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Horizontal legend positioned at top-right
    """

    fig.update_layout( 
        # Hover settings
        hovermode='x unified',
        autosize=False,
        width=700,
        height=500,

        # Title settings
        title={
            'text': title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },

        # X range dropdown menu
        updatemenus=[dict(
            type="dropdown",
            direction="up",
            x=0, y=0, 
            xanchor="left", 
            yanchor="bottom", 
            pad={"r": -10, "t": 0, "b": 0, "l": 0},  # padding around outside of button
            font={"size": 12},
            showactive=True,
            buttons=[dict(label="Bandpass", method="relayout",
                    args=[{"yaxis.autorange": False,"xaxis.autorange": False, "xaxis.range": [1.398,1.954], "yaxis.range":yrange}]),
                dict(label="Zoomed", method="relayout",
                    args=[{"yaxis.autorange": False,"xaxis.autorange": False, "xaxis.range": xrange, "yaxis.range":yrange}]),
                dict(label="Full", method="relayout",
                    args=[{"yaxis.autorange": True,"xaxis.autorange": True}])
            ],
            active=1,
        )],

        # Y-axis settings
        yaxis=dict(
            title=ytitle,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            type="log",
            range =  yrange,
            linewidth=1, linecolor='black', mirror=True, showline=True
        ),
        
        # X-axis settings
        xaxis=dict(
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            showgrid=True,
            hoverformat=".2f",
            range =  xrange,
            linewidth=1, linecolor='black', mirror=True, showline=True,
            domain=[0, 0.98]
        ),

        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=.95,
            bordercolor = "black",
            borderwidth =1
        )
    )


def apply_gw_freq_layout_no_buttons(fig, title = "needs a title", yrange = [-23.7,-19.9],xrange =[1,3],ytitle="Strain Noise [1/HZ]"):
    """
    Apply a standardized layout template for gravitational wave strain frequency data plots with no buttons.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    yrange : list[float, float], optional
        Log range for y-axis as [minimum, maximum] values.
        Given for log scale plot, actual plot y-range will be [1*10^minimum,1*10^maximum] 
        (default: [-23.7,-19.9]) -> actual range [10^-23.7,10^-19.9]
    xrange : list[float, float], optional
        Log range x-axis for zoomed plot as [minimum, maximum] values.
        Given for log scale plot, actual plot x-range will be [1*10^minimum,1*10^maximum] 
        (default: [1,3]) -> actual range [10,1000] (Hz)
    ytitle : str, optional
        Title for the y-axis of the plot (default: "Strain Noise [1/HZ]")
        
    Notes
    -----
    This function adds:
    - Data-specific y-axis scaling and labels
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Horizontal legend positioned at top-right
    """

    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        autosize=False,
        width=700,
        height=500,

        # Title settings
        title={
            'text': title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },

        # Y-axis settings
        yaxis=dict(
            title=ytitle,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            type="log",
            range =  yrange,
            linewidth=1, linecolor='black', mirror=True, showline=True
        ),
        
        # X-axis settings
        xaxis=dict(
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            showgrid=True,
            hoverformat=".2",
            range =  xrange,
            linewidth=1, linecolor='black', mirror=True, showline=True,
            domain=[0, 0.98]
        ),

        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=.95,
            bordercolor = "black",
            borderwidth =1
        )
    )


def apply_gw_1_model_comparision_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from one detector against user generated model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    datetime_center : datetime, optional
        Center time for the plot and zoom controls (default: GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned Horizontal legend
    """

    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        hoversubplots="axis",
        width=700,
        height=650,
        
        # Title settings
        title={
            'text': title,
            'y': 0.9,
            'x': .25,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },

        # Y-axis settings
        yaxis=
        dict(title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        
        xaxis=dict(
            #rangeslider=dict(visible=True),
            title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='bottom',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.98],
            autorange= False,
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),

        
        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=.98,
            borderwidth=1, bordercolor='black'
        ),
    )


def apply_gw_2_model_comparision_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from two detectors against user generated model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    datetime_center : datetime, optional
        Center time for the plot and zoom controls (default: GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned Horizontal legend
    """

    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        #hoversubplots="axis",
        width=700,
        height=650,
        
        # Title settings
        title={
            'text': title,
            'y': .95,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },

        # Y-axis settings
        yaxis=
        dict(title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        yaxis2=dict(
            title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        
        xaxis=dict(
            #rangeslider=dict(visible=True),
            #title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='top',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.98],
            autorange= False,
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),

        xaxis2=dict(
            #rangeslider=dict(visible=True),
            title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.98],
            autorange= False,
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),
        
        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=.5,
            borderwidth=1, bordercolor='black'
        ),
    )


def apply_gw_3_model_comparision_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from three detectors against user generated model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    datetime_center : datetime, optional
        Center time for the plot and zoom controls (default: GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned Horizontal legend
    """

    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        #hoversubplots="axis",
        width=700,
        height=650,
        
        # Title settings
        title={
            'text': title,
            'y': 1.0,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },
        
        # Y-axis settings
        yaxis=
        dict(title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        yaxis2=dict(
            title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        yaxis3=dict(
            title="Normalized Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
        
        # X-axis settings
        xaxis=dict(
            #rangeslider=dict(visible=True),
            #title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='top',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.98],
            autorange= False,
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),
        xaxis2=dict(
            #rangeslider=dict(visible=True),
            #title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', showline=True,mirror=True,
            autorange= False,
            domain=[0, 0.98],
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),
        xaxis3=dict(
            #rangeslider=dict(visible=True),
            title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.98],
            autorange= False,
            range=[datetime_center-timedelta(seconds=.04), datetime_center+timedelta(seconds=.11)]
        ),
        
        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=.5,
            borderwidth=1, bordercolor='black'
        ),
    )


def add_GW_trace_subplot(fig,x,y,color,name,row=1,col=1,alpha=1.0):
    """
    Add single gravitational wave strain data trace to a plotly figure subplot.
    
    Adds time series trace using the provided x and y arrays to a timeseries 
    Plotly figure with datetime format. Uses standard GW detector color 
    and label with resampling for web performance.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to add trace to
    x : ndarray
        The array of times to plot (expecting: data_dictionary[ifo].times.value)
    y : ndarray
        The array of values to plot (expecting: data_dictionary[ifo].value)
    color : str
        The color used for the trace (expecting: color_dictionary[ifo])
    name : str
        Label used for the subplot (expecting: "Livingston", "Hanford", or "Virgo")
    row : int, optional
        row index of subplot where trace is added (default: 1)
    col : int, optional
        column index of subplot where trace is added (default: 1)
    alpha : float, optional
        opacity value used for trace (default: 1.0)
        
    Notes
    -----
    The function automatically:
    - Converts GPS times to UTC datetime objects for proper x-axis display
    - Limits display to 60,000 samples for optimal performance
    - Enables view-based resampling when using FigureResampler

    """

    times = x                                       #(array of GPS seconds)
    t = Time(times, format='gps')                   # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime   # type: ignore    # numpy array of Python datetimes   
                                  
    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=color,
        showlegend=True,
        name=name,
        opacity=alpha
            
    ),
    hf_x = x_datetime,                              #FigureResampler args
    hf_y = y,                               
    limit_to_view=True,
    row=row,
    col=col,
    max_n_samples = 60000                           #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )


def multiplot1_apply_gw_strain_layout(fig, timeseries_title = "needs a title",y_timeseries_title="y need a title",legend_loc =(.97,.9),  datetime_center = Time(1242442967.444, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from one detector against MAP parameter model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    y_timeseries_title : str, optional
        y-axis title (default: "y needs a title")
    legend_loc : (float,float), optional
        coordinate location of legend on plot (default: (.97,.9))
    datetime_center : datetime, optional
        Center time for the plot (default: shifted GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned legend
    """
    fig.update_layout(        
            
            width=700,
            height=500,
            hovermode='x unified',

                    # Title settings
            title={
            'text': timeseries_title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },
        
            yaxis=dict(
            title=y_timeseries_title,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            #tickangle = 90,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),

            xaxis=dict(
            #rangeslider=dict(visible=True),
            title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', mirror=True, showline=True,
            domain=[0, 0.97]
        ),

            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=legend_loc[1],
                        xanchor="right",
                        x=legend_loc[0],borderwidth=1, bordercolor='black'
                    )
            
        )


def multiplot2_apply_gw_strain_layout(fig, timeseries_title = "needs a title",y_timeseries_title="y need a title",legend_loc =(.9,.45),  datetime_center = Time(1242442967.444, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from two detectors against MAP parameter model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    y_timeseries_title : str, optional
        y-axis title (default: "y needs a title")
    legend_loc : (float,float), optional
        coordinate location of legend on plot (default: (.9,.45))
    datetime_center : datetime, optional
        Center time for the plot (default: shifted GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned legend
    """
    fig.update_layout(        
            
            width=700,
            height=500,
            hovermode='x unified',

                    # Title settings
            title={
            'text': timeseries_title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },
        
            yaxis=dict(
            title=y_timeseries_title,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            #tickangle = 90,
            hoverformat=".3e",
            mirror=True,
            side='left',
            #linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),

            xaxis=dict(
            #rangeslider=dict(visible=True),
            #title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='top',
            linewidth=1, linecolor='black', showline=True,#mirror=True,
            domain=[0, 0.97]),

            xaxis2 = dict(
            #rangeslider=dict(visible=True),
            title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.97]),

            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=legend_loc[1],
                        xanchor="right",
                        x=legend_loc[0],borderwidth=1, bordercolor='black'
                    )
            
        )
    fig.update_yaxes(showline=True, mirror=True, linecolor="black", linewidth=1) #backup to get outside lines to show


def multiplot3_apply_gw_strain_layout(fig, timeseries_title = "needs a title",y_timeseries_title="y need a title",legend_loc =(.9,.45),  datetime_center = Time(1242442967.444, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare gravitational wave strain data from three detectors against MAP parameter model.
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    title : str, optional
        Plot title (default: "needs a title")
    y_timeseries_title : str, optional
        y-axis title (default: "y needs a title")
    legend_loc : (float,float), optional
        coordinate location of legend on plot (default: (.9,.45))
    datetime_center : datetime, optional
        Center time for the plot (default: shifted GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned legend
    """
    fig.update_layout(        
            
            width=700,
            height=500,
            hovermode='x unified',

                    # Title settings
            title={
            'text': timeseries_title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },
        
            yaxis=dict(
            title=y_timeseries_title,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            #tickangle = 90,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
            yaxis2=dict(
            #title=y_timeseries_title,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            #tickangle = 90,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),
            yaxis3=dict(
            #title=y_timeseries_title,
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            #tickangle = 90,
            hoverformat=".3e",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
        ),

            xaxis=dict(
            #rangeslider=dict(visible=True),
            #title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='top',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.97]),

            xaxis2 = dict(
            #rangeslider=dict(visible=True),
            #title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='bottom',
            #linewidth=1, linecolor='black', showline=True,#mirror=True,
            domain=[0, 0.97]),

            xaxis3 = dict(
            #rangeslider=dict(visible=True),
            title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            linewidth=1, linecolor='black', showline=True,mirror=True,
            domain=[0, 0.97]),

            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=legend_loc[1],
                        xanchor="left",
                        x=legend_loc[0],borderwidth=1, bordercolor='black'
                    )
            
        )
    #fig.update_yaxes(title=y_timeseries_title,showline=True, mirror=True, linecolor="black", linewidth=1) #backup to get outside lines to show


def Apply_SNR_layout(fig, Title = "Signal to Noise Ratio",  datetime_center = Time(1242442967.4, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template to compare detected gravitational wave Signal to Noise Ratios for the three detectors
        
    Parameters
    ----------
    fig : plotly.graph_objects.Figure or plotly_resampler.FigureResampler
        The Plotly figure object to apply the layout to. Can be either a 
        standard Figure or a FigureResampler for handling large datasets.
    Title : str, optional
        Plot title (default: "Signal to Noise Ratio")
    datetime_center : datetime, optional
        Center time for the plot (default: shifted GW190521 event time)
        
    Notes
    -----
    This function adds:
    - Unified hover mode with scientific notation formatting
    - Standardized axis styling with gridlines and borders
    - Correctly positioned legend
    """
    fig.update_layout(
        hovermode='x unified',

        title={
                'text': Title,
                'y': 0.9,
                'x': .5,
                'xanchor': 'center',
                'yanchor': 'top',
                'automargin': True
            },

            xaxis=dict(
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='bottom',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            #domain=[0, 0.98]
            ),

            xaxis2=dict(
            title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", 
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='bottom',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            ),

            xaxis3=dict(
            type="date",
            #nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0],
            side='bottom',
            linewidth=1, linecolor='black', showline=True,mirror=True,
            ),

            yaxis=dict(
            title="Signal to Noise Ratio",
            fixedrange=False,
            hoverformat=".3f",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,),

            yaxis2=dict(
            #title="Signal to Noise Ratio",
            fixedrange=False,
            hoverformat=".3f",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,),

            yaxis3=dict(
            #title="Signal to Noise Ratio",
            fixedrange=False,
            hoverformat=".3f",
            mirror=True,
            side='left',
            linewidth=1, linecolor="black", showline=True,
            showgrid=True,
            ),

            legend=dict(
                            orientation="v",
                            #yanchor="bottom",
                            #y=.9,
                            #xanchor="left",
                            #x=.5,
                            borderwidth=1, bordercolor='black'
                        )
    )
