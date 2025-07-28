import streamlit as st

st.set_page_config(
    page_title="Base_page",
    page_icon="",
)

pg = st.navigation([st.Page("testpage1.py"),st.Page("testpage2.py"),st.Page("testpage3.py")])
pg.run()