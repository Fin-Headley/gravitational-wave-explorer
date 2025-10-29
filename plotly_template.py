"""
Plotly layout template for GW strain data plots
"""
import streamlit as st
from datetime import timedelta
from astropy.time import Time
from plotly_resampler import FigureResampler # type: ignore
from data_caching import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def graph_help():
    """
    Standard text for graph help pop-up.
    """
    output_text = """Use the button in the lower right to view preset ranges.   
                    You can hide/show GW Observatories by clicking on their name in the legend.  
                    Click to pan.    
                    Change tools in the top right to use custom zooms.   
                    Double-click to reset axis to full graph."""
    return output_text

def graph_help_no_buttons():
    """
    Standard text for graph help pop-up.
    """
    output_text = """You can hide/show GW Observatories by clicking on their name in the legend.  
                    Click to pan.    
                    Change tools in the top right to use custom zooms.   
                    Double-click to reset axis to full graph."""
    return output_text


def apply_gw_strain_layout(fig, title = "needs a title", datetime_center = Time(1242442967.444, format='gps').utc.datetime, data_range = "pure"): # type: ignore
    """
    Apply a standardized layout template for gravitational wave strain data plots.
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


def add_event_marker(fig, marker_time, marker_name, line_color="green", 
                    theme_text_color=None, theme_bc_color=None):
    """
    Add a vertical event marker to the plot.

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


def add_freq_event_marker(fig, marker_freq, line_color="green"): #unused
    """
    Add a vertical event marker to a frequency plot.
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


def create_new_figure():
    """
    Returns a new FigureResampler figure
    """
    return FigureResampler(resampled_trace_prefix_suffix = ("",""), default_n_shown_samples = 1000, show_mean_aggregation_size= False, create_overview=True)


def plot_traces(fig,data_dictionary,ifos,alpha={"L1":1,"H1":1,"V1":1}):
    """
    Adds traces of the timeseries data from data_dictionary to fig
    """
    colours = load_colours_dict()
    short_labels = load_short_labels_dict()

    for ifo in ifos:

        times = data_dictionary[ifo].times.value          # array of GPS seconds
        t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
        x_datetime = t.utc.datetime            # type: ignore           # numpy array of Python datetimes     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0 
                                        #lets do things in numbers and put calculate date in after
        fig.add_trace(go.Scatter(
            mode='lines',
            line_color=colours[ifo],
            showlegend=True,
            name=short_labels[ifo],
            opacity= alpha[ifo]
        
        ),
        hf_x = x_datetime,
        hf_y = data_dictionary[ifo].value,
        limit_to_view=True,
        max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
        )


def plot_single_trace(fig,data_dictionary,ifo="L1"):
    """
    Adds one timeseries trace from data_dictionary to fig
    """
    colours = load_colours_dict()
    short_labels = load_short_labels_dict()

    times = data_dictionary.times.value          # array of GPS seconds
    t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime           # type: ignore                # numpy array of Python datetimes     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0
                                    #lets do things in numbers and put calculate date in after
    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=colours[ifo],
        showlegend=True,
        name=short_labels[ifo],
    
    ),
    hf_x = x_datetime,
    hf_y = data_dictionary.value,
    limit_to_view=True,
    max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )


def plot_freq_traces(fig,data_dictionary,ifos = ['L1', 'V1', 'H1']):
    """
    Adds traces of the frequencyseries data from data_dictionary to fig
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


def apply_gw_freq_layout(fig, title = "needs a title", yrange = [-23.7,-19.9],xrange =[1,3], theme_text_color=None, theme_bc_color=None,ytitle="Strain Noise [1/HZ]"):
    """
    Apply a standardized frequency layout template for gravitational wave strain data plots.
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
            #rangeslider=dict(visible=True, borderwidth=1), #no rangeslider
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            showgrid=True,
            hoverformat=".3",#"Time: %H:%M:%S.%3f",
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


def apply_gw_freq_layout_no_buttons(fig, title = "needs a title", yrange = [-23.7,-19.9],xrange =[1,3], theme_text_color=None, theme_bc_color=None,ytitle="Strain Noise [1/HZ]"):
    """
    Apply a standardized frequency layout template for gravitational wave strain data plots.
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
            #rangeslider=dict(visible=True, borderwidth=1), #no rangeslider
            title=f"Frequency [Hz]",
            type="log",
            #nticks=15,
            showgrid=True,
            hoverformat=".3",#"Time: %H:%M:%S.%3f",
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


def apply_gw_1_model_comparision_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime, theme_text_color=None, theme_bc_color=None): # type: ignore
    """
    Apply a standardized layout template for gravitational wave strain data plots.
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
            title=f"UTC Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
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


def apply_gw_2_model_comparision_layout(fig, title = "needs a title", datetime_center = Time(1242442967.4, format='gps').utc.datetime, theme_text_color=None, theme_bc_color=None): # type: ignore
    """
    Apply a standardized layout template for gravitational wave strain data plots.
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
    Apply a standardized layout template for gravitational wave strain data plots.
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
    Adds timeseries trace to subplot of fig.
    """
    times = x       #data_dictionary[ifo].times.value          # array of GPS seconds
    t = Time(times, format='gps')          # make an Astropy Time array (GPS scale)
    x_datetime = t.utc.datetime            # type: ignore # numpy array of Python datetimes     Something went wrong here! things are centered in wrong place and also time starts at like 13 not at 0
                                    #lets do things in numbers and put calculate date in after
    fig.add_trace(go.Scatter(
        mode='lines',
        line_color=color,
        showlegend=True,
        name=name,
        opacity=alpha
            
    ),
    hf_x = x_datetime,
    hf_y = y,        #data_dictionary[ifo].value,
    limit_to_view=True,
    row=row,
    col=col,
    max_n_samples = 60000 #set to 200,000 to see full data, should prob set much lower/cut data for better speeds
    )


def multiplot1_apply_gw_strain_layout(fig, timeseries_title = "needs a title",y_timeseries_title="y need a title",legend_loc =(.97,.9),  datetime_center = Time(1242442967.444, format='gps').utc.datetime): # type: ignore
    """
    Apply a standardized layout template for gravitational wave strain data plots.
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
    Apply a standardized layout template for gravitational wave strain data plots.
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
    Apply a standardized layout template for gravitational wave strain data plots.
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
    Apply a standardized layout template for gravitational wave strain data plots.
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
            #title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
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
            #title=f"Time on {datetime_center.strftime('%a, %dst %b, %Y')}", #since {str(t0).format('fits')}",
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
