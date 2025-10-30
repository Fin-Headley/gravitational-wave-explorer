import streamlit as st

st.set_page_config(
    page_title="Base_page",
    page_icon="",
)

pg = st.navigation([st.Page("1-Welcome_page.py"),
                    st.Page("pages/2-Exploring_GW_Data.py"),
                    st.Page("pages/3-Noise_correction.py"),
                    st.Page("pages/4-Processing_Data.py"),
                    st.Page("pages/5-My_Data.py"),
                    st.Page("pages/6-Modeling_GWs.py"),
                    st.Page("pages/7-Model_playground.py"),
                    st.Page("pages/8-Statistical_Sampling.py"),
                    st.Page("pages/9-Posterior_Visualization.py"),
                    st.Page("pages/10-Results.py"),
                    
                    ])



pg.run()