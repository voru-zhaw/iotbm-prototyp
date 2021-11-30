# core modules
import os
from datetime import date

# 3rd party modules
import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from babel.numbers import format_decimal

# custom modules
from languages import localization
from tools import loader
from models import payment_model, productivity_model_beta_dist


def show():

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # styling
    css = loader.get_css('css/simulator.css')
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # layout
    col1, col2 = st.columns([4, 1])

    # ========================================================================================================== classic

    with col2:

        # upfront payment slider
        st.markdown('<br>', unsafe_allow_html=True)
        upfront_payment = st.slider(_('Upfront payment [CHF]'), 0, st.session_state['machine']['costs'],
                                    int(st.session_state['machine']['costs']/3),
                                    step=10000)

        # interest rates slider
        interest_rates = 0.03
        # st.markdown('<br>', unsafe_allow_html=True)
        # interest_rates = st.slider(_('Interest rates [%]'), 0.0, 10.0, 3.0, step=0.01) / 100

        # amortization slider
        amortization = 1000
        # st.markdown('<br>', unsafe_allow_html=True)
        # amortization = st.slider(_('Amortization per month'), 0, 10000, 1000, step=500)

    # ================================================================================================ production models

    # check if list of production models is initiated
    if 'production_models' not in st.session_state:
        st.session_state['production_models'] = list()

    # production model form
    with col2:
        with st.expander(_('Production Models')):

            # select new or existing model
            model_list = [_('New')] + [pm.name for pm in st.session_state['production_models']]
            selected_model = st.selectbox(_('Select'), options=model_list, index=0, key='production_model_select')

            # create default production model object
            model_object = productivity_model_beta_dist.Productivity_Model_Beta_Dist()
            model_object.name = 'new_model'

            # check if new model or not
            if selected_model == _('New'):

                # load pre-defined and compatible payment models
                models = st.session_state['production_all']
                # compatible = get_compatible_models(models)
                compatible = models
                model_list = [_('None')]
                if not compatible.empty:
                    model_list += list(compatible['Name'])

                # pre-defined production model selection
                predefined = st.selectbox(label=_('Predefined Models'), options=model_list,
                                          key='predefined-production-models')

                # check if pre-defined model was selected
                if predefined != _('None'):

                    # set pre-definitions
                    predefined_model = compatible[compatible['Name'] == predefined].iloc[0]
                    model_object.target_util_mean = predefined_model[models.columns[2]]
                    model_object.target_util_std = predefined_model[models.columns[3]]
                    model_object.rampup_time = predefined_model[models.columns[7]]
                    model_object.target_util_rampup_mean = predefined_model[models.columns[8]]
                    model_object.target_util_rampup_std = predefined_model[models.columns[9]]*predefined_model[models.columns[8]]
                    model_object.name = predefined_model[models.columns[1]]

            else:

                # get selected model
                for pm in st.session_state['production_models']:
                    if pm.name == selected_model:
                        model_object = pm

            # create form
            with st.form(key='production-model-form'):

                # time parameters
                max_units_per_hour = st.number_input(label=_('Units/Hour'),
                                                     value=model_object.max_units_per_hour,
                                                     help=_('Maximal produced units per hour'))
                hours_per_day = st.number_input(label=_('Hours/Day'),
                                                value=model_object.hours_per_day,
                                                help=_('Number of hours per day during which the production runs'))
                days_per_month = st.number_input(label=_('Days/Month'),
                                                 value=model_object.days_per_month,
                                                 help=_('Average number of days per month during which the production runs'))
                duration = st.number_input(label=_('Duration [months]'),
                                           value=model_object.duration,
                                           help=_('Duration of the simulation given in months'))

                # utilization
                target_util_mean = st.number_input(label=_('Target utilization mean [%]'),
                                                   value=int(model_object.target_util_mean*100),
                                                   step=1,
                                                   help=_('Average machine utilization during operation hours in percentage')) / 100
                target_util_std = st.number_input(label=_('Target utilization rel. std [%]'),
                                                  value=model_object.target_util_std*100,
                                                  step=0.1,
                                                  help=_('Fluctuation of machine utilization during operation hours in percentage')) / 100

                # ramp up
                ramp_up_time = st.number_input(label=_('Ramp-up time [months]'),
                                               value=model_object.rampup_time,
                                               help=_('Duration of the ramp up given in months'))
                target_util_ramp_up_mean = st.number_input(label=_('Utilization mean at start of ramp-up [%]'),
                                                           value=int(model_object.target_util_rampup_mean*100),
                                                           step=1,
                                                           help=_('Average machine utilization at start of ramp-up in percentage')) / 100
                target_util_ramp_up_std = st.number_input(label=_('Utilization rel. std at start of ramp-up [%]'),
                                                          value=model_object.target_util_rampup_std/model_object.target_util_rampup_mean*100,
                                                          step=0.1,
                                                          help=_('Fluctuation of machine utilization at start of ramp-up in percentage of the average utilization')) / 100

                # model name
                name = st.text_input(_('Model Name'), value=model_object.name)

                # submit button
                if selected_model == _('New'):

                    # add button
                    if st.form_submit_button(_('Add')):

                        # check if model name already exists
                        if name in [pm.name for pm in st.session_state['production_models']]:
                            st.error(_('name already exists'))
                        else:
                            # add new model
                            model_object.max_units_per_hour = max_units_per_hour
                            model_object.hours_per_day = hours_per_day
                            model_object.days_per_month = days_per_month
                            model_object.duration = duration
                            model_object.target_util_mean = target_util_mean
                            model_object.target_util_std = target_util_std
                            model_object.rampup_time = ramp_up_time
                            model_object.target_util_rampup_mean = target_util_ramp_up_mean
                            model_object.target_util_rampup_std = target_util_ramp_up_std*target_util_ramp_up_mean
                            model_object.name = name
                            st.session_state['production_models'].append(model_object)
                            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

                else:

                    # update existing model
                    if st.form_submit_button(_('Update')):

                        # update selected model
                        for index, pm in enumerate(st.session_state['production_models']):
                            if pm.name == selected_model:
                                st.session_state['production_models'][index].max_units_per_hour = max_units_per_hour
                                st.session_state['production_models'][index].hours_per_day = hours_per_day
                                st.session_state['production_models'][index].days_per_month = days_per_month
                                st.session_state['production_models'][index].duration = duration
                                st.session_state['production_models'][index].target_util_mean = target_util_mean
                                st.session_state['production_models'][index].target_util_std = target_util_std
                                st.session_state['production_models'][index].rampup_time = ramp_up_time
                                st.session_state['production_models'][index].target_util_rampup_mean = target_util_ramp_up_mean
                                st.session_state['production_models'][index].target_util_rampup_std = target_util_ramp_up_std
                                st.session_state['production_models'][index].name = name
                                raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

                    # delete existing model
                    if st.form_submit_button(_('Delete')):
                        for index, pm in enumerate(st.session_state['production_models']):
                            if pm.name == selected_model:
                                st.session_state['production_models'].pop(index)
                                raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

    # =================================================================================================== payment models

    # check if list of payment models is initiated
    if 'payment_models' not in st.session_state:
        st.session_state['payment_models'] = list()

    # payment model form
    with col2:
        with st.expander(_('Payment Models')):

            # select new or existing model
            model_list = [_('New')] + [pm.name for pm in st.session_state['payment_models']]
            selected_model = st.selectbox(_('Select'), options=model_list, index=0, key='payment_model_select')

            # create default payment model object
            model_object = payment_model.Payment_Model()

            # check if new model or not
            if selected_model == _('New'):

                # load pre-defined and compatible payment models
                models = st.session_state['payment_all']
                compatible = get_compatible_models(models)
                model_list = [_('None')]
                if not compatible.empty:
                    model_list += list(compatible['Name'])

                # pre-defined payment model selection
                predefined = st.selectbox(label=_('Predefined Models'), options=model_list,
                                          key='predefined-payment-models')

                # check if pre-defined model was selected
                if predefined != _('None'):

                    # set pre-definitions
                    predefined_model = compatible[compatible['Name'] == predefined].iloc[0]
                    model_object.payment_upfront = predefined_model['Payment upfront']
                    model_object.payment_per_month = predefined_model['Payment / month']
                    model_object.payment_per_production_unit = predefined_model['Payment / production unit']
                    model_object.name = predefined_model['Name']

            else:

                # get selected model
                for pm in st.session_state['payment_models']:
                    if pm.name == selected_model:
                        model_object = pm

            # create form
            with st.form(key='payment-model-form'):

                # payment per month
                fix = st.number_input(label=_('Payment per month'),
                                      value=model_object.payment_per_month,
                                      help=_('fixed monthly flat rate'))

                # payment per unit
                ppu = st.number_input(label='PPU',
                                      value=model_object.payment_per_production_unit,
                                      help='prize per unit')

                # model name
                name = st.text_input(_('Model Name'), value=model_object.name)

                # submit button
                if selected_model == _('New'):

                    # add button
                    if st.form_submit_button(_('Add')):

                        # check if model name already exists
                        if name in [pm.name for pm in st.session_state['payment_models']]:
                            st.error(_('name already exists'))
                        else:
                            # add new model
                            # model_object.payment_upfront = upfront
                            model_object.payment_per_month = fix
                            model_object.payment_per_production_unit = ppu
                            model_object.name = name
                            st.session_state['payment_models'].append(model_object)
                            raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

                else:

                    # update existing model
                    if st.form_submit_button(_('Update')):

                        # update selected model
                        for index, pm in enumerate(st.session_state['payment_models']):
                            if pm.name == selected_model:
                                # st.session_state['payment_models'][index].payment_upfront = upfront
                                st.session_state['payment_models'][index].payment_per_month = fix
                                st.session_state['payment_models'][index].payment_per_production_unit = ppu
                                st.session_state['payment_models'][index].name = name
                                break
                        raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

                    # delete existing model
                    if st.form_submit_button(_('Delete')):
                        for index, pm in enumerate(st.session_state['payment_models']):
                            if pm.name == selected_model:
                                st.session_state['payment_models'].pop(index)
                                break
                        raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

    # =================================================================================================== list and plots

    with col1:

        # check if there are model combinations
        if len(st.session_state['payment_models']) > 0 and len(st.session_state['production_models']) > 0:

            cumsum1 = st.empty()  # figure
            refsum = st.empty()  # classic model
            cumsum2 = st.empty()  # table

            st.markdown('<br><hr><br>', unsafe_allow_html=True)

            plot_type = st.radio(_('Plot type'), ['boxplot', 'line chart'])

            fig_cumsum = go.Figure()
            fig_units = go.Figure()
            fig_rate = go.Figure()

            # colors
            colors = px.colors.sequential.Rainbow
            color_index = 0
            color_delta = 2

            # compute classic payment
            n_months = st.session_state['production_models'][0].duration
            months = list(range(1, n_months+1))
            months_rev = months[::-1]
            classic = compute_classic_payment(n_months, upfront_payment, interest_rates, amortization,
                                              st.session_state['machine']['Maintenance cost / month'],
                                              st.session_state['machine']['costs'])

            fig_cumsum.add_trace(go.Scatter(x=months, y=classic,
                                            line_color='rgb(255,0,0)',
                                            name=_('classic'),
                                            showlegend=True))

            cumsum_list = f'''| Simulation | Production Model | Payment Model | {_('Cumulative Costs')} | {_('Difference')} |
                              |------------|------------------|---------------|-------------------------|------------------:|'''

            refsum.markdown(f'''**{_('classic')}**: **{format_decimal(classic[-1], format='#,##0.00', locale='de_CH')} CHF**''')

            # loop through the production models
            min_costs = -1
            for prd_id, prd_model in enumerate(st.session_state['production_models']):

                # compute units per month
                n_units = prd_model.get_results()['number_of_units']
                n_units_2d = np.vstack(n_units)
                n_units_mean = np.mean(n_units_2d, 0)
                n_units_std = np.std(n_units_2d, 0)
                n_units_upper = n_units_mean+(1.96*n_units_std)
                n_units_lower = n_units_mean-(1.96*n_units_std)
                n_units_lower = n_units_lower[::-1]

                if plot_type == 'line chart':

                    fig_units.add_trace(go.Scatter(
                        x=months + months_rev,
                        y=np.hstack([n_units_upper, n_units_lower]),
                        fill='toself',
                        fillcolor=f'rgba({colors[color_index][4:-1]},0.2)',
                        line_color=f'rgba({colors[color_index][4:-1]},0)',
                        showlegend=False,
                        name=prd_model.name))

                    fig_units.add_trace(go.Scatter(
                        x=months,
                        y=n_units[0],
                        line=dict(color=f'rgba({colors[color_index][4:-1]},0.5)', width=1, dash='dash'),
                        line_shape='spline',
                        showlegend=False,
                        name=prd_model.name))

                    fig_units.add_trace(go.Scatter(
                        x=months,
                        y=n_units_mean,
                        line_color=colors[color_index],
                        showlegend=True,
                        name=prd_model.name))

                else:

                    fig_units.add_trace(go.Box(
                        y=n_units[0],
                        fillcolor=f'rgba({colors[color_index][4:-1]},0.5)',
                        line_color=colors[color_index],
                        name=prd_model.name))

                # loop through the payment models
                for pay_id, pay_model in enumerate(st.session_state['payment_models']):

                    # simulation name
                    sim_name = f'''sim-{prd_id}-{pay_id}'''

                    # set payment upfront
                    pay_model.payment_upfront = upfront_payment

                    # compute monthly rates
                    pay_model.number_of_units = n_units[0]
                    # rates = pay_model.get_results()
                    rates = pay_model.payment_per_month + n_units[0] * pay_model.payment_per_production_unit
                    rates_mean = pay_model.payment_per_month + n_units_mean * pay_model.payment_per_production_unit
                    rates_upper = pay_model.payment_per_month + n_units_upper * pay_model.payment_per_production_unit
                    rates_lower = pay_model.payment_per_month + n_units_lower * pay_model.payment_per_production_unit

                    # compute cumulative costs
                    costs = [x + pay_model.payment_upfront for x in np.cumsum(rates_mean)]
                    costs_upper = [x + pay_model.payment_upfront for x in np.cumsum(rates_upper)]
                    costs_lower = [x + pay_model.payment_upfront for x in np.cumsum(rates_lower[::-1])][::-1]

                    # add entry to the list
                    cost_diff = costs[-1]-classic[-1]
                    color = 'green' if cost_diff < 0 else 'red'
                    cumsum_list += f'''\n| {sim_name} | {prd_model.name} | {pay_model.name} | {format_decimal(costs[-1], format='#,##0.00', locale='de_CH')} CHF | **<span style="color: {color};">{format_decimal(costs[-1]-classic[-1], format='#,##0.00', locale='de_CH')}</span> CHF** | '''

                    # check if this is the "best" combination of models (best = lowest costs)
                    if min_costs == -1 or costs[-1] < min_costs:
                        min_costs = costs[-1]
                        if 'best' not in st.session_state:
                            st.session_state['best'] = dict()
                        st.session_state['best']['prd'] = prd_model
                        st.session_state['best']['pay'] = pay_model

                    fig_cumsum.add_trace(go.Scatter(
                        x=months + months_rev,
                        y=np.hstack([costs_upper, costs_lower]),
                        fill='toself',
                        fillcolor=f'rgba({colors[color_index][4:-1]},0.2)',
                        line_color=f'rgba({colors[color_index][4:-1]},0)',
                        showlegend=True,
                        name=sim_name + _('_confidence')
                    ))

                    fig_cumsum.add_trace(go.Scatter(
                        x=months,
                        y=costs,
                        line_color=colors[color_index],
                        name=sim_name + _('_mean'),
                        showlegend=True))

                    if plot_type == 'line chart':

                        fig_rate.add_trace(go.Scatter(
                            x=months + months_rev,
                            y=np.hstack([rates_upper, rates_lower]),
                            fill='toself',
                            fillcolor=f'rgba({colors[color_index][4:-1]},0.2)',
                            line_color=f'rgba({colors[color_index][4:-1]},0)',
                            showlegend=False,
                            name=sim_name))

                        fig_rate.add_trace(go.Scatter(
                            x=months,
                            y=rates,
                            line=dict(color=f'rgba({colors[color_index][4:-1]},0.5)', width=1, dash='dash'),
                            line_shape='spline',
                            showlegend=False,
                            name=prd_model.name))

                        fig_rate.add_trace(go.Scatter(
                            x=months,
                            y=rates_mean,
                            line_color=colors[color_index],
                            showlegend=True,
                            name=sim_name))

                    else:

                        fig_rate.add_trace(go.Box(
                            y=rates,
                            fillcolor=f'rgba({colors[color_index][4:-1]},0.5)',
                            line_color=colors[color_index],
                            name=sim_name))

                    # update color
                    color_index += color_delta

            fig_cumsum.update_layout(
                title=_('Cumulative Costs'),
                xaxis_title=_('Months'),
                legend_title=_('Simulations'),
                xaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=6
                ),
                yaxis=dict(
                    tickmode='linear',
                    tick0=-1,
                    dtick=100000
                )
            )
            cumsum1.plotly_chart(fig_cumsum, use_container_width=True)
            cumsum2.markdown(cumsum_list, unsafe_allow_html=True)

            if plot_type == 'line chart':

                fig_units.update_layout(
                    title=_('Units per Month'),
                    xaxis_title=_('Months'),
                    yaxis_title=_('Units per Month'),
                    legend_title=_('Simulations'),
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=6
                    )
                )

                fig_rate.update_layout(
                    title=_('Monthly Rates'),
                    xaxis_title=_('Months'),
                    yaxis_title=_('Costs per Month [CHF]'),
                    legend_title=_('Simulations'),
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=6
                    )
                )

            else:

                fig_units.update_layout(
                    title=_('Units per Month'),
                    xaxis_title=_('Simulation'),
                    yaxis_title=_('Units per Month')
                )

                fig_rate.update_layout(
                    title=_('Monthly Rates'),
                    xaxis_title=_('Simulation'),
                    yaxis_title=_('Costs per Month [CHF]')
                )

            st.plotly_chart(fig_rate, use_container_width=True)
            st.plotly_chart(fig_units, use_container_width=True)

            # create report
            # create_report(fig_cumsum)


@st.cache
def get_compatible_models(models) -> pd.DataFrame:

    machine_id = st.session_state['machine']['Id']

    rows_to_drop = []
    for index, row in models.iterrows():
        if isinstance(row['Compatible Machines'], str):
            if not any(machine_id in m for m in row['Compatible Machines'].split(',')):
                rows_to_drop.append(index)
    compatible = models.drop(rows_to_drop)

    # return compatible models
    return compatible


@st.cache
def compute_classic_payment(n_months, upfront, rates, amortization, maintenance, costs):

    monthly_rates = []
    costs -= upfront
    for i in range(n_months):
        rate = 0
        if costs > 0:
            rate = costs*rates + amortization
            if i >= 24:
                rate += maintenance
            costs -= amortization
        monthly_rates.append(rate)
        print(monthly_rates)

    # monthly_rates = [(costs-upfront)*rates]*n_months
    return [x + upfront for x in np.cumsum(monthly_rates)]


def create_report(fig):

    # set translation function
    _ = localization.get_translation('settings', st.session_state['language'])

    # clear folder
    folder = 'tmp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        os.unlink(file_path)

    # create fig image
    file_path = os.path.join(folder, 'fig1.png')
    plotly.io.write_image(fig, file=file_path, format='png')
    fig = file_path

    # get current date
    today = date.today()
    current_date = today.strftime("%d.%m.%Y")

    # create PDF object
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    file_path = os.path.join(folder, 'report.pdf')

    # header
    pdf.image('resources/images/agathon_mantra.png', x=10, y=20, h=3)
    pdf.image('resources/images/logo.jpg', x=160, h=12)

    # title
    pdf.set_font('Arial', 'U', 14)
    pdf.text(10, 40, f'EaaS / PPU Report vom {current_date}')

    # basic information
    pdf.set_font('Arial', '', 10)
    pdf.text(10, 50, _('Customer') + ':')
    pdf.text(100, 50, f'''{st.session_state['customer']['name'][0]}''')
    pdf.text(10, 55, _('Machine') + ':')
    pdf.text(100, 55, f'''{st.session_state['machine']['Name']}''')
    pdf.text(10, 60, _('Financing Price') + ':')
    pdf.text(100, 60, f'''CHF {st.session_state['machine']['costs']} ({_('total costs according to configuration')})''')
    pdf.text(10, 65, _('Upfront Payment') + ':')
    pdf.text(100, 65, f'''CHF {st.session_state['best']['pay'].payment_upfront} ({_('freely selectable')})''')
    pdf.text(10, 70, _('Contract Duration') + ':')
    pdf.text(100, 70, f'''{st.session_state['best']['prd'].duration} {_('months')} ({_('minimum 24 months')})''')
    pdf.text(10, 75, _('Optional purchase price after contract duration') + ':')
    pdf.text(100, 75, f'''CHF''')

    # simulation
    pdf.text(10, 85, _('Overview (graphic) from the calculation:'))
    pdf.image(fig, x=10, y=90, h=120)
    pdf.set_x(10)
    pdf.set_y(210)
    pdf.write(5, 'Wie die oben gezeigte Grafik verdeutlicht, sind für ihren Anwendungsfall die geringsten Kosten verbunden mit dem Modell "' +
              f'''{st.session_state['best']['pay'].name}".''')

    # monthly costs
    pdf.text(10, 230, 'Ihre monatlichen Kosten betragen somit:')
    pdf.set_font('Arial', 'B', 10)
    pdf.text(10, 240, 'Grundgebühr:')
    pdf.text(70, 240, f'''CHF {st.session_state['best']['pay'].payment_per_month}.-   ({_('inkl. Anteil Servicegebühr')})''')
    pdf.text(10, 245, 'Gebühr pro Spindelstunde:')
    pdf.text(70, 245, f'''CHF {st.session_state['best']['pay'].payment_per_production_unit}.-''')

    # contact
    pdf.set_font('Arial', '', 10)
    pdf.text(10, 255, f'''{_('Gerne unterstützen wir Sie im weiteren Vorgehen.')}''')
    pdf.text(10, 265, 'Kontaktdaten Area Sales Manager')
    pdf.text(100, 265, 'Kontaktdaten Head of Subscription')

    # PDF object -> PDF file
    pdf.output(file_path, 'F')
