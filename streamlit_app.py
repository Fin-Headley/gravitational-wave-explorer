import streamlit as st

st.set_page_config(
    page_title="Base_page",
    page_icon="",
)

pg = st.navigation([st.Page("1-Welcome_page.py"),
                    st.Page("2-Exploring_GW_Data.py"),
                    st.Page("3-Noise_correction.py"),
                    st.Page("4-Processing_Data.py"),
                    st.Page("5-My_Data.py"),
                    st.Page("6-Modeling_GWs.py"),
                    st.Page("7-Model_playground.py"),
                    st.Page("8-Statistical_Sampling.py"),
                    st.Page("9-Posterior_Visualization.py"),
                    st.Page("10-Results.py"),
                    
                    ])

pg.run()