import json

import streamlit as st
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie


# Layout
st.set_page_config(
    page_title="Talk to Any Website!",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🗣️"
    )

show_pages([
    Page("main_page.py","Main"),
    Page("login.py","Login"),
    Page("chatbot.py","Chatbot"),
])

hide_pages(['Main', 'Login', 'Chatbot'])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    col1, col2, col3 = st.sidebar.columns(3)
    if col1.button('My Page'):
        st.session_state.page = 'mypage'
        switch_page('Login')
    if col2.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = 'Login'
        switch_page('Main')
else:
    if st.sidebar.button('Login'):
        switch_page('Login')

st.markdown("""
<style>
.big-font {
    font-size:80px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('Talk to Any Website!', ['Main', 'Chatbot'],
        icons=['house', 'chat-dots'], menu_icon='robot', default_index=0)
    lottie = load_lottiefile("chatbot.json")
    st_lottie(lottie,key='loc')

if selected == 'Main':
    st.title('🗣️ Talk to Any Website!')
    st.subheader('A personalized website assistant that communicates in natural language')
    st.divider()
    st.image('main_image.png')

if selected == 'Chatbot':
    switch_page('Chatbot')