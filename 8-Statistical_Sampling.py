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

st.set_page_config(page_title="Statistical Sampling", page_icon="📈",layout="wide")

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

ifos = ['L1', 'V1','H1']
########################################################################

st.title("Statistical Parameter Estimation")

st.header('How do we get "correct" Physical Parameters from a model')

st.markdown("""
One of the main tools used to estimate source properties Gravitational Wave Astrophysics is Bayesian inference.

Lets do a brief recap of Bayes' theorem:

""")

st.latex(r"""
P(\lambda \mid x) = \frac{P(x \mid \lambda) \, P(\lambda)}{P(x)}
""")

st.latex(r"""
\text{where: } 
P(\lambda \mid x) \text{ is the posterior, } \;
P(x \mid \lambda) \text{ is the likelihood, } \;
P(\lambda) \text{ is the prior, and } \;
P(x) \text{ is the evidence.}
""")


st.markdown(r"""
$\lambda$ represents the unknown parameters of the model that we are trying to estimate.
            
$x$ is the observed data, the Strain data from the detectors.

$P(\lambda \mid x)$ is the posterior, which describes the probability of our model parameters given the observed data.
            
$P(x \mid \lambda)$ is the likelyhood, which is the probability of observing the data, given all of the parameters have value \lambda.

$P(\lambda)$ is the prior, which is our knowledge of the parameters before encountering any data.
            
$P(x)$ is the evidence. For single model parameter estimation this is simply a normalization factor.

The aim is to construct a posterior distribution function.   
Once we have a posterior distribution function we then sample the posterior distribution in order to find high probability estimates for the unknown parameters. 

""")

st.header('Defining the functions')

st.markdown(r"""
Before functions are defined there is some setup as the likelyhood is calculated in frequency space.
The first step is to do a fourier transform of the Strain data, as the likelyhood will be calculated in frequency space.
""")

with st.expander("Preliminary setup"):
    st.code(
    """
    from astropy import units as u
    from gwosc.datasets import event_gps
    from gwpy.timeseries import TimeSeries

    gps_time = event_gps('GW190521')
    segment = ((gps)-16, (gps)+16)        #get a 32 second long segment containing the GW190521 event

    pure_data = {}     #create a dictionary to hold the timeseries arrays
    pure_data['L1'] =  TimeSeries.fetch_open_data('L1', *segment) #Ligo_Livingston
    pure_data['H1'] =  TimeSeries.fetch_open_data('H1', *segment) #Ligo_Hanford
    pure_data['V1'] =  TimeSeries.fetch_open_data('V1', *segment) #Virgo

    ifos = ['L1', 'V1','H1'] #A list of the three detectors to iterate over

    ASD_data = {} #create dictionary to hold the ASD for each detector
    for ifo in ifos:  #create the ASD for each detector
        ASD_data[ifo] = pure_data[ifo].asd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.)

        
    PSD_data = {} #create dictionary to hold the PSD for each detector
    for ifo in ifos:  #create the PSD for each detector
        PSD_data[ifo] = pure_data[ifo].psd(fftlength=4.,window=('tukey',1./4.),method='welch',overlap=2.)
    #The PSD or Power Spectral Density is the equivalent to the ASD squared

    # FFT the data once, ahead of time
    sf={} #dictionary for the FFT frequency space strain data

    data_bp_c = {}  #dictionary of data that has been bandpass and cropped (but not whitened)

    for ifo in ifos:
        data_bp_c[ifo] = pure_data[ifo].bandpass(25.,90.).crop(gps-2,gps+2)

        sf[ifo] = data_bp_c[ifo].average_fft(window=('tukey',1./4.))*data_bp_c[ifo].duration.value/2
    """
    )

st.markdown(r"""
With this taken care of, a likelyhood function can be defined. In practice, the functions are all created in Log space.

Here is my Likelyhood function:
""")

with st.expander("Log Likelyhood function"):

    st.code(
"""
def loglikelihood(param, sf=sf, f_lower=10.0): 
    #takes in a parameter list, the frequency space strain data, and an lower frequency limit

    #forces units get clean output
    logl = 0.0 * u.Hz**2 # type: ignore

    #uses the gen_template() function defined in Modeling GWs to create a model and fit it to the three detectors
    template = gen_template(param, delta_t=data_bp_c['H1'].dt.value ,f_lower=f_lower)
    
    for ifo in ifos:

        # zero out the frequencies below f_lower
        sf_hp = sf[ifo].crop(start=f_lower)
        psd_hp = psd[ifo].crop(start=f_lower)

        #apply a FFT to the model to convert it into a frequency series
        #then zero out the frequencies below f_lower
        hf = template[ifo].average_fft(window=('tukey',1./4.))*template[ifo].duration.value/2
        hf_hp = hf.crop(start=f_lower)

        # Check for zero-length or bad data
        if len(hf_hp) == 0 or len(sf_hp) == 0 or len(psd_hp) == 0:
            return -np.inf
        
        #computing inner products
        h_dot_h  = 4 * np.real((hf_hp * hf_hp.conjugate() / psd_hp).sum() * hf_hp.df)
        h_dot_s  = 4 * np.real((sf_hp * hf_hp.conjugate() / psd_hp).sum() * sf_hp.df)

        #log likelyhood for a single detector
        logl += h_dot_s - h_dot_h/2

    #sanity check
    if not np.isfinite(logl):
        return -np.inf
    
    #returns log likelyhood
    return float(logl.to_value('Hz2'))
"""

)
    

st.markdown(
r"""
We could now put in variables and try and maximize the likehood function, but lets define a prior and posterior so that we can sample the posterior distribution for our parameter estimates.

The Prior function serves two purposes. 
It preforms a check to make sure that any later sampler picks values that are valid for get_td_waveform().
It also adjusts any priors for parameters that we know to be non-uniform.

We expect GW sources to be uniformly distrubuted in space, therefore an adjustment is made to take this fact into account.
""")

with st.expander("Log Prior function"):

    st.code(
"""
def logprior(param): #take in param list
    
    logp = 0

    #extracting parameters from the input list
    m1, q, distance, time_shift, phase, ra, dec, inclination, polarization = param

    #check to see that the mass and mass ratio both have valid values
    if m1 <= 0:
        return -np.inf
    if q < 0.05:
        return -np.inf
    if q > .97:
        return -np.inf
    #check to see that ra, phase, polarization all have valid values
    for angle in [ra, phase, polarization]:
        if angle < 0 or angle > 2*np.pi:
            return -np.inf
    #check to see that distance has a valid value
    if distance < 0:
        return -np.inf
    #check to see that inclination has a valid value
    if inclination < 0 or inclination > np.pi:
        return -np.inf
    #check to see that declination has a valid value
    if dec < -np.pi/2 or dec > np.pi/2:
        return -np.inf
    
    #adjust prior to be non uniform, 
    #taking into account that there should be a uniform distrubution
    #of GW events happening in local universe around us
    logp += np.log(np.cos(dec))
    logp += 2*np.log(distance)
    logp += np.log(np.sin(inclination))
    return logp
"""
)

st.markdown(
r"""
Finally, we can create a posterior function.
""")

with st.expander("Log posterior function"):

    st.code(
"""
def logposterior(param):                #take in input parameters
    logpost = logprior(param)           #set value based on prior distribution
    if np.isfinite(logpost):            #if parameters are valid
        logpost += loglikelihood(param) #multiply the prior by the loglikelihood (this is happening in log space)
    return logpost                      #return a value for the posterior
"""
)

st.markdown(
r"""
We can now maximize the posterior function to determine the *Maximum a posteriori* (MAP) parameters.  

The parameters that give a maximized posterior are a "best guess" that takes into account how well the model fits the data, 
while also taking into account any prior knowledge we have for the parameters.

Additionally, it is now possible for us to "sample" the posterior distribution. By sampling the distribution, we are able to quantify uncertainties in our estimates.

I used a Markov chain Monte Carlo (MCMC) sampler in order to sample the posterior distribution.
""")

st.header("MCMC sampling")



with st.expander("MCMC sampling"):

    st.code(
    
"""

import multiprocessing as mp
import emcee
from emcee.moves import StretchMove, DEMove
from emcee.backends import HDFBackend


param_bounds = [ #upper and lower bounds for the parameters
     (80., 200.)          # primary mass
    ,(0.5, .95)           # mass ratio
    ,(500, 5000)          # Lum distance
    ,(.02, .04)           # time_shift
    ,(0, 2*np.pi)         # phase
    ,(0, 2*np.pi)         # right_ascension
    ,(-np.pi/2.,np.pi/2.) # declination
    ,(0,np.pi)            # inclination
    ,(0, 2*np.pi)         # polarization
]

ndim = 9 # number of parameters to sample

nwalkers =  24 # number of chains that will sample parameters

opt = best_fit_parameters.copy() # my best point before sampling

np.random.seed(42) #set random seed for repeat runs

#set each walkers to a slight variation of the current maximum posterior
def random_in_bounds():
    while True:
        # Scale jitter by the magnitude of the parameter, but ensure a minimum jitter
        scale = 1e-2 * np.maximum(np.abs(opt), .1)  # avoid zero jitter
        trial = opt + np.random.randn(ndim) * scale
        if np.all([lo <= x <= hi for x,(lo,hi) in zip(trial, param_bounds)]):
            return trial
p0 = np.array([random_in_bounds() for _ in range(nwalkers)])

# Initialize the backend to save MCMC 
filename = "MCMC_save_data.h5"
backend = HDFBackend(filename)
#backend.reset(nwalkers, ndim)

#list of moves that the walkers can take
moves = [(StretchMove(a=2.0), 0.8), (DEMove(), 0.2)]

#set up multithreading
with mp.Pool() as pool:
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, logposterior, moves=moves, pool=pool, backend=backend)

    nsteps = 100000              # total iterations
    sampler.run_mcmc(p0, nsteps, progress=True)
""")

st.markdown(
r"""
**Note:** *As the Virgo Detector was less sensitive and had a low Signal to Noise Ratio, Virgo data was excluded from the MCMC sampling.
Plots with Virgo data will be shown, but the Virgo Strain data was not used in calculating the combined likelyhood or Posterior values.*

After running the MCMC sampler for 100000 steps, 35426 steps(\*24 walkers) were discarded as burnin to reduce parameter correlation. 
Additionally the sample was thinned in order to save memory, removing every other step. 

This resulted in a combined total sample size of 774,888 parameter combinations.

The results of the MCMC are visualized in the :blue-background[Posterior Visualization] tab. The MAP parameters, with uncertainties, are given in the :blue-background[MCMC results] tab.
""")



