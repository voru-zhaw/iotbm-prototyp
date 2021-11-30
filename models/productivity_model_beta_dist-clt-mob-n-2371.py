import numpy as np


class Productivity_Model_Beta_Dist():
    def __init__(self,
                 id = 1,
                 name = 'new_model',
                 PF_mean = 0.8,
                 PF_std = 0.02,
                 AF_mean = 0.8,
                 AF_std = 0.02,
                 QF_mean = 0.8,
                 QF_std = 0.02,
                 duration = 36,
                 max_units_per_hour = 1,
                 hours_per_day = 16,
                 days_per_month = 25
                ):
        self.id = id,
        self.name = name,
        self.PF_mean = PF_mean
        self.PF_std = PF_std
        self.AF_mean = AF_mean
        self.AF_std = AF_std
        self.QF_mean = QF_mean
        self.QF_std = QF_std
        self.duration = duration
        self.max_units_per_hour = max_units_per_hour
        self.hours_per_day = hours_per_day
        self.days_per_month = days_per_month
        self._recompute()
    
    def _calc_alpha_beta(self, mean, std):
        '''
        Calculates alpha and beta (for beta distribution) from mean and standard deviation.
        '''
        var = std**2
        alpha = mean*(mean*(1-mean)/var-1)
        beta = alpha*(1-mean) / mean
        return alpha, beta

    def _generate_timeseries(self, mean, std, duration):
        '''
        Returns an array with beta distributed values given the mean and standard deviation.
        '''
        alpha, beta = self._calc_alpha_beta(mean, std)
        return np.random.beta(alpha, beta, size=duration)

    def _calc_number_of_units(self, OEE, max_units_per_hour, hours_per_day, days_per_month):

        return np.floor(OEE * max_units_per_hour * hours_per_day * days_per_month)

    def _recompute(self):
        # save a snapshot of the current parameter values
        self._params_dic = {'id' : self.id,
                            'name' : self.name,
                            'PF_mean' : self.PF_mean,
                            'PF_std' : self.PF_std,
                            'AF_mean' : self.AF_mean,
                            'AF_std' : self.AF_std,
                            'QF_mean' : self.QF_mean,
                            'QF_std' : self.QF_std,
                            'duration' : self.duration,
                            'max_units_per_hour' : self.max_units_per_hour,
                            'hours_per_day' : self.hours_per_day,
                            'days_per_month' : self.days_per_month
                            }

        # make beta distributed array
        PF = self._generate_timeseries(self.PF_mean, self.PF_std, self.duration)
        AF = self._generate_timeseries(self.AF_mean, self.AF_std, self.duration)
        QF = self._generate_timeseries(self.QF_mean, self.QF_std, self.duration)
        OEE = PF * AF * QF
        number_of_units = self._calc_number_of_units(OEE, self.max_units_per_hour, self.hours_per_day, self.days_per_month)
    
        self._results = {
            'availability': AF,
            'performance': PF,
            'quality': QF,
            'OEE': OEE,
            'number_of_units': number_of_units,
            }

    def _parameters_changed(self):
        return (self._params_dic['id'] != self.id) | \
               (self._params_dic['name'] != self.name) | \
               (self._params_dic['PF_mean'] != self.PF_mean) | \
               (self._params_dic['PF_mean'] != self.PF_mean) | \
               (self._params_dic['AF_mean'] != self.AF_mean) | \
               (self._params_dic['AF_std'] != self.AF_std) | \
               (self._params_dic['QF_mean'] != self.QF_mean) | \
               (self._params_dic['QF_std'] != self.QF_std) | \
               (self._params_dic['duration'] != self.duration) | \
               (self._params_dic['max_units_per_hour'] != self.max_units_per_hour) | \
               (self._params_dic['hours_per_day'] != self.hours_per_day) | \
               (self._params_dic['days_per_month'] != self.days_per_month)

    def get_results(self):
        if self._parameters_changed():
            self._recompute()
        return self._results  # .copy() to protect against data manipulation from outside.

def test():
    amodel = Productivity_Model_Beta_Dist(PF_mean=0.9)
    mean09 = amodel.get_results()

    amodel.PF_mean = 0.5
    mean05 = amodel.get_results()

if __name__ == '__main__':
    test()

