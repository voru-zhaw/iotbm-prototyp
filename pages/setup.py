# 3rd party module
import streamlit as st

# custom modules
from languages import localization
from tools import loader

import time

# input file
INPUT_FILE = 'database/datamodel.xlsx'
MACHINES_SHEET = 'Machines'
OPTIONS_SHEET = 'Options'
PRODUCTION_SHEET = 'Production Models'
PAYMENT_SHEET = 'Payment Models'


def run():

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # layout
    col1, col2, col3 = st.columns([2, 3, 2])

    # load content
    with col2:
        st.subheader(_('Loading data...'))
        progress_bar = st.progress(0)
        progress_text = st.markdown('')

        # load machines
        progress_text.markdown(_('...machines'))
        time.sleep(0.5)
        st.session_state['machines_all'] = loader.get_data(INPUT_FILE, MACHINES_SHEET)
        st.session_state['machine'] = st.session_state['machines_all'].iloc[0]
        progress_bar.progress(25)

        # load options
        progress_text.markdown(_('...options'))
        time.sleep(0.5)
        st.session_state['options_all'] = loader.get_data(INPUT_FILE, OPTIONS_SHEET)
        progress_bar.progress(50)

        # load production models
        progress_text.markdown(_('...production models'))
        time.sleep(0.5)
        st.session_state['production_all'] = loader.get_data(INPUT_FILE, PRODUCTION_SHEET)
        progress_bar.progress(75)

        # load payment models
        progress_text.markdown(_('...payment models'))
        time.sleep(0.5)
        st.session_state['payment_all'] = loader.get_data(INPUT_FILE, PAYMENT_SHEET)
        progress_bar.progress(100)

        time.sleep(0.2)

    # set default page
    st.session_state['page'] = 'Settings'
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))
