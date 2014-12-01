__author__ = 'Jonas Andersson'

from subprocess import PIPE, Popen
import re
import json
import fileinput
import matplotlib.pyplot as plt

#Global State
config_filename = "sim_config"
inject_rate = re.compile(r"(?P<identifier>injection_rate)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)(?P<semicolon>;)")
avg_packet_latency = re.compile(r"(?P<identifier>Packet latency average)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)")
algorithm_re = re.compile(r"(?P<identifier>routing_function)(?P<assign_op>[ =]+)(?P<algorithm>[a-z_]+)(?P<semicolon>;)")
rates = [round(rate * 0.01, 3) for rate in range(0, 62, 2)]
algorithms = ['dor', 'romm', 'min_adapt', 'valiant']


#Helper Functions
def invoke():
    with Popen(['booksim', config_filename], stdout=PIPE) as simulation:
        overall_stats = False
        with open('simulation', 'wb') as file:
            for line in simulation.stdout:
                if "Overall Traffic" in str(line):
                    overall_stats = True
                if overall_stats:
                    file.write(line)


def get_value():
    with open('simulation', 'r') as file:
        latency = "Nan"
        text = file.read()
        match = avg_packet_latency.search(text)
        if match:
            latency = match.group('value')
        return latency


def update_config(new_rate, alg=None):
    if alg:
        print('Simulating ' + alg + ' algorithm')
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(algorithm_re.sub('routing_function = ' + alg + ';', line), end='')
        return
    print('Injection rate set to ' + new_rate)
    with fileinput.input(config_filename, inplace=True) as config:
        for line in config:
            print(inject_rate.sub('injection_rate = ' + str(new_rate) + ';', line), end='')
    return


def run_simulation():
    data = []
    for rate in rates:
        update_config(str(rate))
        invoke()
        data_point = (rate, get_value())
        data.append(data_point)
    return data


def plot_data(results):
    xlabel = 'Offered Traffic'
    ylabel = 'Avg delay (cycles)'
    for data_set in results:
        x_vals = [x[0] for x in data_set]
        y_vals = [y[1] for y in data_set]
        plt.plot(x_vals, y_vals)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()


def data_file(alg, dat):
    with open(alg, 'w') as file:
        file.write(json.dumps(dat))

#Main Loop
if __name__ == '__main__':
    all_data = []
    for algorithm in algorithms:
        update_config('0.00', alg=algorithm)
        data = run_simulation()
        all_data.append(data)
        data_file(algorithm, data)
    plot_data(all_data)