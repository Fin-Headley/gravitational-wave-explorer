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
                    
                    st.Page("6-Exploring GW Data.py"),
                    st.Page("7-PSD_creation.py"),
                    ])

pg.run()