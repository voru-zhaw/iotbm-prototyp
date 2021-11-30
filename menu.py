# 3rd party modules
import streamlit as st
from PIL import Image

# custom modules
from languages import localization
from tools import loader

# pages
pages = ['Settings', 'Configurator', 'Simulator', 'Report']


def go_to_settings():
    st.session_state['page'] = pages[0]


def go_to_configurator():
    st.session_state['page'] = pages[1]


def go_to_simulator():
    st.session_state['page'] = pages[2]


def go_to_report():
    st.session_state['page'] = pages[3]


def show():

    # styling
    css = loader.get_css('css/menu.css')
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # layout
    col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 0.8, 2, 1, 1, 1, 1, 0.5, 0.6, 1.7, 1])

    # logo
    with col0:
        st.image('resources/images/logo.png', width=120)

    # customer info
    with col2:
        if 'customer' in st.session_state:
            customer = st.session_state['customer']
            st.markdown(f'''{_('Customer')} : {customer['name'][0]}  
            {_('Country')}  : {customer['country'][0]}  
            {_('Location')} : {customer['location'][0]} ''')

    # page buttons
    with col3:
        st.markdown('### ')
        st.button(pages[0], on_click=go_to_settings)
    with col4:
        st.markdown('### ')
        st.button(pages[1], on_click=go_to_configurator)
    with col5:
        st.markdown('### ')
        st.button(pages[2], on_click=go_to_simulator)
    with col6:
        st.markdown('### ')
        st.button(pages[3], on_click=go_to_report)

    # sales manager
    with col8:
        st.image('resources/images/person.png')
    with col9:
        st.markdown(f'''Area Sales Manager  
                    **Peter Muster**''')

    # language selector
    with col10:
        languages = list(localization.languages.keys())
        index = languages.index(st.session_state['language'])
        language = st.selectbox('', languages, index=index, format_func=localization.get_language)
        if st.session_state['language'] != language:
            st.session_state['language'] = language
            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))
    st.markdown('___')
