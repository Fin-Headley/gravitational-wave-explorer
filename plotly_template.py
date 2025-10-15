"""
Plotly layout template for GW strain data plots
"""
import streamlit as st
from datetime import timedelta
from astropy.time import Time
from plotly_resampler import FigureResampler # type: ignore
from data_caching import *
import plotly.graph_objects as go

def apply_gw_strain_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime, theme_text_color=None, theme_bc_color=None):
    """
    Apply a standardized layout template for gravitational wave strain data plots.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure or FigureResampler
        The figure object to apply the layout to
    title : str
        The title for the plot (e.g., 'Observed GW Strain Data', 'Bandpassed GW Strain Data')
    datetime_center : datetime
        The center datetime for the zoom buttons
    t0 : datetime
        The reference time for the x-axis title
    theme_text_color : str, optional
        Streamlit theme text color (will use st.get_option if not provided)
    theme_bc_color : str, optional
        Streamlit theme background color (will use st.get_option if not provided)
    
    Returns:
    --------
    None (modifies fig in place)
    """


    # Get theme colors if not provided
    if theme_text_color is None:
        theme_text_color = st.get_option('theme.textColor')
    if theme_bc_color is None:
        theme_bc_color = st.get_option('theme.backgroundColor')
    
    fig.update_layout(
        # Hover settings
        hovermode='x unified',
        #hoversubplots="axis",
        width=700,
        height=600,

        # X range dropdown menu
        updatemenus=[dict(
            type="dropdown",
            direction="up",
            active=4,
            x=0, y=0, 
            xanchor="left", 
            yanchor="bottom", 
            pad={"r": -10, "t": 0, "b": 0, "l": 0},  # padding around outside of button
            font={"size": 12},
            showactive=True,
            buttons=[
                dict(label="±0.1 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.1), datetime_center+timedelta(seconds=.1)]}]),
                dict(label="±0.2 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.2), datetime_center+timedelta(seconds=.2)]}]),
                dict(label="±.5 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=.5), datetime_center+timedelta(seconds=.5)]}]),
                dict(label="±1 s", method="relayout",
                    args=[{"xaxis.autorange": False, "xaxis.range": [datetime_center-timedelta(seconds=1), datetime_center+timedelta(seconds=1)]}]),
                dict(label="Full", method="relayout",
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
            title="Strain",
            fixedrange=False,
            showexponent="all",
            exponentformat="power",
            #nticks=5,
            hoverformat=".3e"
        ),
        
        # X-axis settings
        xaxis=dict(
            #rangeslider=dict(visible=True),
            title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
            type="date",
            nticks=8,
            showgrid=True,
            hoverformat="Time: %H:%M:%S.%3f",
            autotickangles = [0, 30, 45],
        ),
        
        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1
        )
    )


def add_event_marker(fig, marker_time, marker_name, line_color="green", 
                    theme_text_color=None, theme_bc_color=None):
    """
    Add a vertical event marker to the plot.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure or FigureResampler
        The figure object to add the marker to
    event_time : datetime
        The center datetime for the event marker
    marker_name : str
        text for event marker
    line_color : str, optional
        Color of the event marker line (default: "green")
    theme_text_color : str, optional
        Streamlit theme text color (will use st.get_option if not provided)
    theme_bc_color : str, optional
        Streamlit theme background color (will use st.get_option if not provided)
    
    Returns:
    --------
    None (modifies fig in place)
    """
    
    # Get theme colors if not provided
    if theme_text_color is None:
        theme_text_color = st.get_option('theme.textColor')
    if theme_bc_color is None:
        theme_bc_color = st.get_option('theme.backgroundColor')
    
    fig.add_vrect(
        x0=marker_time, 
        x1=marker_time + timedelta(microseconds=1), 
        line_color=line_color,
        line_width=3,
        annotation=dict(
            text=marker_name,
            font=dict(
                size=12,
                color=theme_text_color,
            ),
            bgcolor=theme_bc_color,
            opacity=1,
            y=.85,
            xanchor="left", 
            yanchor="bottom",
            showarrow=False,
        ),
        annotation_position="outside top right",
    )


def add_freq_event_marker(fig, marker_freq, line_color="green"):
    """
    Add a vertical event marker to a frequency plot.
    did have text too but that was taken out
    """
    fig.add_vline(
        x=marker_freq, 
        line_color=line_color,
        line_width=3,
    )

def add_freq_event_shading(fig, freq_start, freq_end, fillcolor="chartreuse",opacity=0.25,line_width=0):
    """
    Add a shading box to to a frequency plot.
    """
    fig.add_vrect(x0=freq_start
                  ,x1=freq_end
                  ,fillcolor=fillcolor
                  ,opacity=opacity
                  ,line_width=line_width)



# Convenience function that combines both layout and event marker
def setup_gw_plot(fig, title, datetime_center, event_marker_color="green", 
                 event_offset_seconds=0, theme_text_color=None, theme_bc_color=None):
    """
    Complete setup for a GW strain plot with layout and event marker.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure or FigureResampler
        The figure object to set up
    title : str
        The title for the plot
    datetime_center : datetime
        The center datetime for the zoom buttons and event marker
    event_marker_color : str, optional
        Color of the event marker line (default: "green")
    event_offset_seconds : float, optional
        Offset in seconds from the center time for event marker (default: 0)
    theme_text_color : str, optional
        Streamlit theme text color (will use st.get_option if not provided)
    theme_bc_color : str, optional
        Streamlit theme background color (will use st.get_option if not provided)
    
    Returns:
    --------
    None (modifies fig in place)
    """
    apply_gw_strain_layout(fig, title, datetime_center, theme_text_color, theme_bc_color)
    add_event_marker(fig, datetime_center, event_marker_color, event_offset_seconds, 
                    theme_text_color, theme_bc_color)
    



def create_new_figure():
    return FigureResampler(resampled_trace_prefix_suffix = ("",""), default_n_shown_samples = 1000, show_mean_aggregation_size= False, create_overview=True)


def plot_traces(fig,data_dictionary,ifos):
    colours = import_colours_dict()
    short_labels = import_short_labels_dict()

    for ifo in ifos:

        times = data_dictionary[ifo].times.value          # array of GPS seconds
        t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
        x_datetime = t.utc.datetime            # numpy array of Python datetimes     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0
                                        #lets do things in numbers and put calculate date in after
        fig.add_trace(go.Scatter(
            mode='lines',
            line_color=colours[ifo],
            showlegend=True,
            name=short_labels[ifo],
        
        ),
        hf_x = x_datetime,
        hf_y = data_dictionary[ifo].value,
        limit_to_view=True,
        max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )



def plot_freq_traces(fig,data_dictionary,ifos = ['L1', 'V1', 'H1']):

    colours = import_colours_dict()
    short_labels = import_short_labels_dict()

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


def apply_gw_freq_layout(fig, title = "needs a title", yrange = list,xrange =[1,3], theme_text_color=None, theme_bc_color=None,ytitle="Strain Noise [1/&#8730;HZ]"):
    """
    Apply a standardized frequency layout template for gravitational wave strain data plots.
    
    Parameters:
    -----------
    
    Returns:
    --------
    None (modifies fig in place)
    """

    # Get theme colors if not provided
    if theme_text_color is None:
        theme_text_color = st.get_option('theme.textColor')
    if theme_bc_color is None:
        theme_bc_color = st.get_option('theme.backgroundColor')
    
    fig.update_layout( #change to fig.update_layout and put in function
        # Hover settings
        hovermode='x unified',
        autosize=False,
        width=700,
        height=600,

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
        
        # Title settings

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
            rangeslider=dict(visible=True, borderwidth=1),
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            showgrid=True,
            hoverformat=".3",#"Time: %H:%M:%S.%3f",
            range =  xrange,
            linewidth=1, linecolor='black', mirror=True, showline=True
        ),

        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1,
            bordercolor = "black",
            borderwidth =1
        )
    )


def apply_gw_fourier_layout(fig, title = "needs a title", yrange = list,xrange =[50,400], theme_text_color=None, theme_bc_color=None,ytitle="Phase"):
    """
    Apply a standardized frequency layout template for gravitational wave strain data plots.
    
    Parameters:
    -----------
    
    Returns:
    --------
    None (modifies fig in place)
    """

    # Get theme colors if not provided
    if theme_text_color is None:
        theme_text_color = st.get_option('theme.textColor')
    if theme_bc_color is None:
        theme_bc_color = st.get_option('theme.backgroundColor')
    
    fig.update_layout( #change to fig.update_layout and put in function
        # Hover settings
        hovermode='x unified',
        autosize=False,
        width=700,
        height=600,

        # Title settings
        title={
            'text': title,
            'y': 0.9,
            'x': .5,
            'xanchor': 'center',
            'yanchor': 'top',
            'automargin': True
        },

        
        # Title settings

        # Y-axis settings
        yaxis=dict(
            #rangeslider=dict(visible=True, borderwidth=1),
            title=ytitle,
            #fixedrange=False,
            #showexponent="all",
            #exponentformat="power",
            #nticks=5,
            hoverformat=".3e",
            type="linear",
            range =  yrange,
            linewidth=1, linecolor='black', mirror=True, showline=True
        ),
        
        # X-axis settings
        xaxis=dict(
            #rangeslider=dict(visible=True, borderwidth=1),
            title=f"Frequency [Hz]",
            type="linear",
            #nticks=15,
            showgrid=True,
            hoverformat=".3",#"Time: %H:%M:%S.%3f",
            range =  xrange,
            linewidth=1, linecolor='black', mirror=True, showline=True
        ),

        # Legend settings
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1,
            bordercolor = "black",
            borderwidth =1
        )
    )

def plot_both_fourier_freq_traces(fig,ifo = 'L1'):

    raw_data = import_raw_data()

    strain_fft = raw_data[ifo].average_fft()
    strain_fft_win = raw_data[ifo].average_fft(window=('tukey',1./4.))

    fig.add_trace(go.Scatter( #add in windowed points
        mode='markers',
        name="Tukey window",
        showlegend=True,
        ),
        hf_x = strain_fft_win.frequencies,
        hf_y = np.angle(strain_fft_win),
        limit_to_view=True,
        hf_marker_color="red",
        hf_marker_size = 3,
        max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )

    fig.add_trace(go.Scatter( #add in un-windowed points
        mode='markers',
        name="no window",
        showlegend=True,
        ),
        hf_x = strain_fft.frequencies,
        hf_y = np.angle(strain_fft),
        limit_to_view=True,
        hf_marker_color="blue",
        hf_marker_size = 3,
        max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )



def plot_window_psd_trace(fig,data_dictionary,ifo ='L1',color="black",name="Window"):

    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=color,
        showlegend=True,
        name=name,
    ),
    hf_x = data_dictionary[ifo].frequencies,
    hf_y = data_dictionary[ifo].value,
    limit_to_view=True,
    max_n_samples = 100000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )
