# 3rd party modules
import streamlit as st
import pandas as pd
import numpy as np
from babel.numbers import format_decimal

# custom modules
from languages import localization
from tools import loader


# builds/shows the configurator page
def show():

    # styling
    css = loader.get_css('css/configurator.css')
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # layout
    col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 0.5, 3, 1, 3, 1, 3])

    # ========================================================================================================== machine
    with col1:

        # get machines
        machines = st.session_state['machines_all']

        # machine configuration
        machine = st.session_state['machine']

        # let user select machine
        index = machines.index[machines['Name'] == machine['Name']].values[0].item()
        selection = st.selectbox(_('Machine'), machines['Name'], index=index)
        machine = machines[machines['Name'] == selection].iloc[0]

        # update selection
        if machine['Id'] != st.session_state['machine']['Id']:
            st.session_state['machine'] = machine
            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

        # present selected machine
        st.image(machine['Picture'], machine['Name'])

    # ========================================================================================================== Machine
    with col3:

        # machine description
        st.markdown(f'''#### {_('Description')}''')
        st.markdown(f'''{machine['Description']}''')

        # machine cost
        machine['Price'] = st.number_input(_('Price')+' [CHF]', min_value=0.0, value=float(machine['Price']),
                                           step=100.0, format='%.2f')
        # st.markdown(f'''#### {_('Price')}''')
        # st.markdown(f'''{format_decimal(machine['Price'], format='#,##0.00', locale='de_CH')} CHF''')

        # installation cost
        machine['Installation cost'] = st.number_input(_('Installation cost')+' [CHF]',
                                                       min_value=0.0, value=float(machine['Installation cost']),
                                                       step=100.0, format='%.2f')
        # st.markdown(f'''#### {_('Installation cost')}''')
        # st.markdown(f'''{format_decimal(machine['Installation cost'], format='#,##0.00', locale='de_CH')} CHF''')

        # maintenance cost
        machine['Maintenance cost / month'] = st.number_input(_('Maintenance cost')+' [CHF]', min_value=0.0,
                                                              value=float(machine['Maintenance cost / month']),
                                                              step=100.0, format='%.2f',
                                                              help=_('per month | starting after 24 months'))
        # st.markdown(f'''#### {_('Maintenance cost')}\n<span style="color:gray">''' +
        #             f'''{_('(per month | starting after 24 months)')}</span>''', unsafe_allow_html=True)
        # st.markdown(f'''{format_decimal(machine['Maintenance cost / month'],
        #                                format='#,##0.00', locale='de_CH')} CHF''')

        # update selection
        if (
                machine['Price'] != st.session_state['machine']['Price'] or
                machine['Installation cost'] != st.session_state['machine']['Installation cost'] or
                machine['Maintenance cost / month'] != st.session_state['machine']['Maintenance cost / month']
        ):
            st.session_state['machine'] = machine
            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

    # ========================================================================================================== Options
    with col5:

        # get options
        options = st.session_state['options_all']

        # options configuration
        if 'options' not in st.session_state:
            st.session_state['options'] = pd.DataFrame()

        # available options and categories
        compatible = get_compatible_options(machine['Id'], options)
        categories = compatible['Category'].unique()

        # show options and update configuration
        st.markdown(f'''### {_('Options')}''')
        for category in categories:
            # st.markdown(f'#### {category}s')
            for index, option in compatible[compatible['Category'] == category].iterrows():

                # check if options exists in session state
                value = not st.session_state['options'].empty and \
                        option['Name'] in st.session_state['options'].values

                # get user input
                checked = st.checkbox(f"{option['Name']}", value=value)

                # case 1: user selected new option
                if checked and not value:
                    st.session_state['options'] = st.session_state['options'].append(option)
                    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

                # case 2: user de-selected existing option
                if not checked and value:
                    st.session_state['options'] = st.session_state['options'].drop(index=index)
                    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

    # ============================================================================================================ Costs
    with col7:

        # init costs
        costs = 0

        # header
        st.markdown(f'''### {_('Costs')}''')
        table = f'''| {_('Item')} | {_('Price')} (CHF) |  
        |-----|-----:| '''

        # machine
        table += f'''\n| {machine['Name']} | {format_decimal(machine['Price'], format='#,##0.00', locale='de_CH')} |'''
        costs += machine['Price']

        # installation costs
        table += f'''\n| {_('Installation cost')} | {format_decimal(machine['Installation cost'], format='#,##0.00', locale='de_CH')} |'''
        costs += machine['Installation cost']

        # selected options
        for index, option in st.session_state['options'].iterrows():
            table += f'''\n| {option['Name']} | {format_decimal(option['Payment upfront'], format='#,##0.00', locale='de_CH')} |'''
            costs += option['Payment upfront']

        # show table and total costs
        st.markdown(table)
        st.markdown(f'''### Total = {format_decimal(costs, format='#,##0.00', locale='de_CH')}''')
        st.session_state['machine']['costs'] = np.int(costs)


@st.cache
def get_compatible_options(machine_id, options):

    rows_to_drop = []
    for index, row in options.iterrows():
        if isinstance(row['Compatible machines'], str):
            if not any(machine_id in m for m in row['Compatible machines'].split(',')):
                rows_to_drop.append(index)
    options = options.drop(rows_to_drop)

    return options
