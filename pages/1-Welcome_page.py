import streamlit as st

st.set_page_config(page_title="Welcome Page", page_icon="👋",layout="wide")

st.title("Welcome!")

st.markdown(
'''
This web app is designed to breakdown the process of Gravitational Wave parameter estimation.

Use the tabs on the left of the screen to move to different pages.
''')


st.title("Contents:")
st.markdown(
""" 
:blue-background[Welcome page] - This page! Welcome!

:blue-background[Exploring GW data] - How to fetch data from the Gravitational Wave Open Science Center, and a brief exploration of the GW190521 data.

:blue-background[Noise Correction] - An introduction bandpass filters and whitened data.

:blue-background[Processing Data] - Interactive plot! Try and find the hidden Gravitational Waves by picking your own bandpass range and whitening the data.

:blue-background[My Data] - The processed Interferometer Stain data I used for my models.

:blue-background[Modeling GWs] - An introduction to how to model Gravitational Waves.

:blue-background[Model playground] - Interactive plot! Try and find your own parameters to model the GW190521 event.

:blue-background[Statistical Sampling] - An introduction to Bayesian inference.

:blue-background[Posterior Visualization] - Visualization of the 2D parameter space for my model.

:blue-background[Results] - My "best guess" Parameter Estimation for the Black Hole Merger that caused GW190521.
""" 
)

st.header("Some useful terms:")

with st.expander("hello"):
    st.markdown(
'''
This app displays public data from LIGO and Virgo collaborations, downloaded from the Gravitational Wave Open Science Center at https://gwosc.org.
''')


st.header("About this app")
st.markdown(
'''
This app displays public data from LIGO and Virgo collaborations, downloaded from the Gravitational Wave Open Science Center at https://gwosc.org.
''')
