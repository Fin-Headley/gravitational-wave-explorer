import streamlit as st


pg = st.navigation([st.Page("testpage1.py")])
pg.run()

#st.set_page_config(
#    page_title="Hello",
#    page_icon="",
#)


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
