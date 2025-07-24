import streamlit as st

st.set_page_config(
    page_title="Starter Page",
    page_icon="",
)

pg = st.navigation([st.Page("testpage1.py"),st.Page("testpage2.py")])
pg.run()


st.title("Analysis of GW190521")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.markdown(
     """ 
    
    This will be my initial page.

    I will use this as a sudo README.

    I will define pages from here that split out and do different things.
     """ 
    )
