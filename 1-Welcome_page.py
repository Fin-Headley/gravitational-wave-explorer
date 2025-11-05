import streamlit as st

st.set_page_config(page_title="Welcome Page", page_icon="👋",layout="wide")

st.title("Welcome!")

st.markdown(
'''
This web app is designed to breakdown the process of Gravitational Wave parameter estimation using the GW190521 event.

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

with st.expander("A few helpful definitions:"):
    st.markdown(
r'''
:orange-background[Gravitational Waves:] (GWs) Ripples in the fabric of spacetime, often caused by the relative movement of massive astrophysical objects, such as Black Holes.

:orange-background[Interferometer:] A scientific instrument used to detect GWs by measuring the tiny oscillations of space caused by Gravitational Waves.

:orange-background[LIGO:] The "Laser Interferometer Gravitational-wave Observatory". Comprised of two separate US based Interferometers, LIGO Livingston and LIGO Hanford.

:orange-background[Virgo:] European based Gravitational-wave Interferometer. Member of the LIGO-Virgo-KAGRA (LVK) collaboration.

:orange-background[Strain:] A dimensionless quantity that measures the fractional change in length caused by a passing gravitational wave, defined as $h = \Delta L/L$.
''')


st.header("About this app")
st.markdown(
'''
This app displays public data from LIGO and Virgo collaborations, downloaded from the Gravitational Wave Open Science Center at https://gwosc.org.
''')


st.header("About me")
st.markdown(
'''
My name is Fin Headley.

I have an academic background in physics, astronomy, and computer science. I studied Astronomy and
Physics at Boston University before receiving a Master of Science in Data-Intensive Astrophysics 
from Cardiff University. My MSC dissertation was on developing a computational methodology to solve n
on-analytic equations in the field of Numerical Relativity.

The full code for this web app can be found in a public repository on Github.
''')
col1, col2, col3 = st.columns([4,4,6])

with col1:
    st.link_button("My Github","https://github.com/Fin-Headley")

with col2:
    st.link_button("My Linkedin","https://www.linkedin.com/in/fin-headley/")


