import streamlit as st

st.set_page_config(
    page_title="Base_page",
    page_icon="",
)

pg = st.navigation([st.Page("1-Welcome_page.py"),st.Page("2-data_test.py"),st.Page("testpage3.py")])
pg.run()