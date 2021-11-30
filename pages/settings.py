# 3rd-party modules
import streamlit as st
import pandas as pd

# custom modules
from languages import localization
from tools import loader


def show():

    # styling

    css = loader.get_css('css/settings.css')
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # layout
    left, middle, right = st.columns([1, 2, 1])

    # customer form
    with middle:
        with st.form(key='customer_form'):

            # customer settings
            if 'customer' not in st.session_state:
                st.session_state['customer'] = pd.DataFrame({'name': [''], 'country': [''], 'location': ['']})
            customer = st.session_state['customer']

            # inputs
            name = st.text_input(_('Customer'), value=customer['name'][0],
                                 help=_('Customer name'))
            country = st.text_input(_('Country'), value=customer['country'][0],
                                    help=_('Country of legal entity'))
            location = st.text_input(_('Machine Location'), value=customer['location'][0],
                                     help=_('Country of installation and usage'))
            submit = st.form_submit_button(_('Save'))

    # confirmation
    if submit:
        if customer['name'][0] != name or customer['country'][0] != country or customer['location'][0] != location:
            st.session_state['customer']['name'][0] = name
            st.session_state['customer']['country'][0] = country
            st.session_state['customer']['location'][0] = location
            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))


def next_page():
    st.session_state['page'] = 'Configurator'
