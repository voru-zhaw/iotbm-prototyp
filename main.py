# 3rd party modules
import streamlit as st
from PIL import Image

# custom modules
from languages import localization
from tools import footer
from pages import settings, configurator, simulator, report, setup
import menu

# webpage configuration
title = 'Prototype'
logo = Image.open('resources/images/favicon.jpg')
st.set_page_config(page_title=title, page_icon=logo, layout='wide', initial_sidebar_state='auto')

# default language
if 'language' not in st.session_state:
    st.session_state['language'] = 'de'  # default language is "Deutsch"

# set translation function
_ = localization.get_translation('settings', st.session_state['language'])

# add menu with the page buttons
menu.show()

# add footer with ZHAW and HSG logos
footer.footer()

# show active page
if 'page' not in st.session_state:
    setup.run()
else:
    if st.session_state['page'] == menu.pages[0]:
        settings.show()
    elif st.session_state['page'] == menu.pages[1]:
        configurator.show()
    elif st.session_state['page'] == menu.pages[2]:
        simulator.show()
    elif st.session_state['page'] == menu.pages[3]:
        report.show()
    else:
        st.error('Something has gone terribly wrong.')

