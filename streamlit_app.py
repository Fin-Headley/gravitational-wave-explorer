import streamlit as st

st.set_page_config(
    page_title="Base_page",
    page_icon="",
)

pg = st.navigation([st.Page("1-Welcome_page.py"),
                    st.Page("2-data_test.py"),
                    st.Page("3-updated_page_test.py"),
                    st.Page("4-working_graphs.py"),
                    st.Page("5-psd_plotting.py"),
                    
                    st.Page("6-Exploring_GW_Data.py"),
                    st.Page("7-Noise_correction.py"),
                    st.Page("8-Processing_Data.py"),
                    st.Page("14-Processed_Data.py"),
                    st.Page("9-Modeling_GWs.py"),
                    st.Page("10-MCMC_display_tests.py"),
                    st.Page("11-MCMC_results.py"),
                    st.Page("12-Q_transform_testing.py"),
                    st.Page("13-Extra_plots.py"),


                    ])

pg.run()