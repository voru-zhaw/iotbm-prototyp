import numpy as np


class Productivity_Model_Beta_Dist():
    def __init__(self,
                 target_util_mean=1,
                 target_util_std=0.1,
                 target_util_rampup_mean=1,
                 target_util_rampup_std=0.1,
                 rampup_time=12,
                 duration=36,
                 max_units_per_hour=1,
                 hours_per_day=16,
                 days_per_month=25
                 ):

        self.target_util_mean = target_util_mean
        self.target_util_std = target_util_std
        self.target_util_rampup_mean = target_util_rampup_mean
        self.target_util_rampup_std = target_util_rampup_std
        self.rampup_time = rampup_time
        self.duration = duration
        self.max_units_per_hour = max_units_per_hour
        self.hours_per_day = hours_per_day
        self.days_per_month = days_per_month
        self._recompute()

    def _calc_alpha_beta(self, mean, std):
        """
        Calculates alpha and beta (for beta distribution) from mean and standard deviation.
        """
        var = std**2
        alpha = mean*(mean*(1-mean)/var-1)
        beta = alpha*(1-mean) / mean
        return alpha, beta

    def _generate_timeseries(self, mean, std, mean_rampup, std_rampup, rampup_time, duration, n_runs=10000):
        """
        Returns an array with beta distributed values given the mean and standard deviation.
        """
        timeseries_n_runs = []
        for i in range(n_runs):
            # Caluclation during RampUp
            # Calculate Linear function for rampup
            def rampup_gradient(x): return (mean-mean_rampup) / rampup_time * x + mean_rampup
            timeseries_rampup_gradient = rampup_gradient(np.arange(1, rampup_time+1))
            # Alpha and beta calculation exceptions-> only the mean is used without std
            if mean_rampup == 1 or mean_rampup+std_rampup >= 1 or mean_rampup == 0 or mean_rampup-std_rampup <= 0:
                pass
            else:
                for i in range(rampup_time):
                    alpha_rampup, beta_rampup = self._calc_alpha_beta(timeseries_rampup_gradient[i], std_rampup)
                    timeseries_rampup_gradient[i] = np.random.beta(alpha_rampup, beta_rampup)
            # Calculations after RampUp
            # Alpha and beta calculation exceptions
            if mean == 1 or mean == 0 or std == 0 or mean+std > 1 or mean - std <= 0:
                timeseries = np.repeat(mean_rampup, rampup_time)
            else:
                alpha, beta = self._calc_alpha_beta(mean, std)
                timeseries = np.random.beta(alpha, beta, size=duration - rampup_time)

            timeseries = np.append(timeseries_rampup_gradient, timeseries)
            timeseries_n_runs.append(timeseries)
        return timeseries_n_runs

    def _calc_number_of_units(self, OEE, max_units_per_hour, hours_per_day, days_per_month):

        return [np.floor(i * max_units_per_hour * hours_per_day * days_per_month) for i in OEE]

    def _recompute(self):
        # save a snapshot of the current parameter values
        self._params_dic = {'target_util_mean': self.target_util_mean,
                            'target_util_std': self.target_util_std,
                            'target_util_rampup_mean': self.target_util_rampup_mean,
                            'target_util_rampup_std': self.target_util_rampup_std,
                            'rampup_time': self.rampup_time,
                            'duration': self.duration,
                            'max_units_per_hour': self.max_units_per_hour,
                            'hours_per_day': self.hours_per_day,
                            'days_per_month': self.days_per_month
                            }

        # make beta distributed array
        OEE = self._generate_timeseries(self.target_util_mean,
                                        self.target_util_std,
                                        self.target_util_rampup_mean,
                                        self.target_util_rampup_std,
                                        self.rampup_time,
                                        self.duration)

        number_of_units = self._calc_number_of_units(
            OEE, self.max_units_per_hour, self.hours_per_day, self.days_per_month)

        self._results = {
            'OEE': OEE,
            'number_of_units': number_of_units,
        }

    def _parameters_changed(self):
        return (self._params_dic['target_util_mean'] != self.target_util_mean) | \
               (self._params_dic['target_util_std'] != self.target_util_std) | \
               (self._params_dic['target_util_rampup_mean'] != self.target_util_rampup_mean) | \
               (self._params_dic['target_util_rampup_std'] != self.target_util_rampup_std) | \
               (self._params_dic['rampup_time'] != self.rampup_time) | \
               (self._params_dic['duration'] != self.duration) | \
               (self._params_dic['max_units_per_hour'] != self.max_units_per_hour) | \
               (self._params_dic['hours_per_day'] != self.hours_per_day) | \
               (self._params_dic['days_per_month'] != self.days_per_month)

    def get_results(self):
        if self._parameters_changed():
            self._recompute()
        return self._results  # .copy() to protect against data manipulation from outside.


def test():
    amodel = Productivity_Model_Beta_Dist(
        target_util_mean=0.2, target_util_rampup_mean=0.5, target_util_rampup_std=0.05, rampup_time=12)
    mean09 = amodel.get_results()

    amodel.PF_mean = 0.5
    mean05 = amodel.get_results()


if __name__ == '__main__':
    test()
