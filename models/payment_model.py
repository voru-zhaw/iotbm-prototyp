import pandas as pd
import numpy as np

class Payment_Model():
    def __init__(self, 
                 id = 1,
                 name = 'new_model',
                 payment_unit = 'currency',
                 production_unit = 'kilogram',
                 time_unit = 'hours',
                 number_of_units = 0,
                 payment_upfront = 0,
                 payment_per_production_time = 0,
                 payment_per_production_unit = 0,
                 payment_per_month = 0,
                 payment_floor_per_month = 0,
                 payment_cap_per_month = 0,
                 min_contract_term = 12,
                 max_contract_term = 12,
                 final_maturity = 'static',
                 description = 0,
                 compatible_machines = 0,
                 compatible_options = 0,
                 service_costs = 0
                 ):

        self.id = id
        self.name = name
        self.payment_unit = payment_unit
        self.production_unit = production_unit
        self.time_unit = time_unit
        self.number_of_units = number_of_units
        self.payment_upfront = payment_upfront
        self.payment_per_production_time = payment_per_production_time
        self.payment_per_production_unit = payment_per_production_unit
        self.payment_per_month = payment_per_month
        self.payment_floor_per_month = payment_floor_per_month
        self.payment_cap_per_month = payment_cap_per_month
        self.min_contract_term = min_contract_term
        self.max_contract_term = max_contract_term
        self.final_maturity = final_maturity
        self.description = description
        self.compatible_machines = compatible_machines
        self.compatible_options = compatible_options
        self.service_costs = service_costs
        self._recompute()

    def _recompute(self):
        # save a snapshot of the current parameter values
        self._params_dic = {'id' : self.id,
                            'name' : self.name,
                            'payment_unit' : self.payment_unit,
                            'production_unit' : self.production_unit,
                            'time_unit' : self.time_unit,
                            'payment_upfront' : self.payment_upfront,
                            'payment_per_production_time' : self.payment_per_production_time,
                            'payment_per_production_unit' : self.payment_per_production_unit,
                            'payment_per_month' : self.payment_per_month,
                            'payment_floor_per_month' : self.payment_floor_per_month,
                            'payment_cap_per_month' : self.payment_cap_per_month,
                            'min_contract_term' : self.min_contract_term,
                            'max_contract_term' : self.max_contract_term,
                            'final_maturity' : self.final_maturity,
                            'description' : self.description,
                            'compatible_machines' : self.compatible_machines,
                            'compatible_options' : self.compatible_options,
                            'service_costs' : self.service_costs
                            }
        # compute the results for the current parameter values
        #TODO#
        self._results = self.payment_per_month + self.payment_per_production_unit * self.number_of_units + self.service_costs

    def _parameters_changed(self):
        return (self._params_dic['id'] != self.id) | \
               (self._params_dic['name'] != self.name) | \
               (self._params_dic['payment_unit'] != self.payment_unit) | \
               (self._params_dic['production_unit'] != self.production_unit) | \
               (self._params_dic['time_unit'] != self.time_unit) | \
               (self._params_dic['payment_upfront'] != self.payment_upfront) | \
               (self._params_dic['payment_per_production_time'] != self.payment_per_production_time) | \
               (self._params_dic['payment_per_production_unit'] != self.payment_per_production_unit) | \
               (self._params_dic['payment_per_month'] != self.payment_per_month) | \
               (self._params_dic['payment_floor_per_month'] != self.payment_floor_per_month) | \
               (self._params_dic['payment_cap_per_month'] != self.payment_cap_per_month) | \
               (self._params_dic['min_contract_term'] != self.min_contract_term) | \
               (self._params_dic['max_contract_term'] != self.max_contract_term) | \
               (self._params_dic['final_maturity'] != self.final_maturity) | \
               (self._params_dic['description'] != self.description) | \
               (self._params_dic['compatible_machines'] != self.compatible_machines) | \
               (self._params_dic['compatible_options'] != self.compatible_options) | \
               (self._params_dic['service_costs'] != self.service_costs)

    def get_results(self):
        if self._parameters_changed():
            self._recompute()
        return self._results  # .copy() to protect against data manipulation from outside.
            

def test():
    pm = Payment_Model(payment_upfront=1000)
    r1000 = pm.get_results()
    # user input
    pm.payment_upfront = 2000
    pm.payment_per_production_unit = 10
    pm.number_of_units = np.array([100, 200, 300])
    pm.service_costs = 100
    r2000 = pm.get_results()

if __name__ == '__main__':
    test()



# def _read_scenarios():
#     return pd.read_excel('def_scenarios_cost_model.xlsx', 'scenarios')

# def _make_dict_from_df(df):
#     return df.to_dict('index')
#
# def test_multi_dict():
#     df_def_scenarios = read_scenarios()
#     dict_def_scenarios = make_dict_from_df(df_def_scenarios)
#     df_res = pd.DataFrame(
#         run_model(**scenario)
#             for _,scenario in dict_def_scenarios.items())
#     return df_res

