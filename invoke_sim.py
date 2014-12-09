__author__ = 'Jonas Andersson'

from subprocess import PIPE, Popen
import re
import json
import fileinput
import matplotlib.pyplot as plt
import csv
from itertools import cycle

#Global State
data_filename = ""
config_filename = "sim_config"
inject_rate = re.compile(r"(?P<identifier>injection_rate)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)(?P<semicolon>;)")
avg_packet_latency = re.compile(r"(?P<identifier>Packet latency average)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)")
algorithm_re = re.compile(r"(?P<identifier>routing_function)(?P<assign_op>[ =]+)(?P<algorithm>[a-z_]+)(?P<semicolon>;)")
num_vcs_re = re.compile(r"(?P<identifier>num_vcs)(?P<assign_op>[ =]+)(?P<value>[0-9]+)(?P<semicolon>;)")
allocator_re = re.compile(r"(?P<identifier>vc_allocator)(?P<assign_op>[ =]+)(?P<method>[a-z_]+)(?P<semicolon>;)")
sw_allocator_re = re.compile(r"(?P<identifier>sw_allocator)(?P<assign_op>[ =]+)(?P<method>[a-z_]+)(?P<semicolon>;)")
traffic_re = re.compile(r"(?P<identifier>traffic)(?P<assign_op>[ =]+)(?P<pattern>[a-z_]+)(?P<semicolon>;)")

rates = [round(rate * 0.001, 3) for rate in range(0, 500, 2)]
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


def update_config(new_rate, alg=None, vc_num=None, alloc=None, traffic=None):
    if traffic:
        print('Traffic pattern set to ' + traffic)
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(traffic_re.sub('traffic = ' + traffic + ';', line), end='')
    if alloc:
        #There has to be a better way to do this
        #If the two sub calls are in the same loop, it fills the config file with garbage
        print('Switch and VC allocation set to ' + alloc)
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(allocator_re.sub('vc_allocator = ' + alloc + ';', line), end='')
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(sw_allocator_re.sub('sw_allocator = ' + alloc + ';', line), end='')
    if vc_num:
        print('Setting number of virtual channels to: ' + str(vc_num))
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(num_vcs_re.sub('num_vcs = ' + str(vc_num) + ';', line), end='')
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


def plot_data(results, legend):
    xlabel = 'Offered Traffic'
    ylabel = 'Avg delay (cycles)'
    title = 'Average Latency vs. Offered Load'
    lines = ["-","--","-.",":"]
    linecycler = cycle(lines)
    for data_set in results:
        x_vals = [x[0] for x in data_set]
        y_vals = [y[1] for y in data_set]
        plt.plot(x_vals, y_vals, next(linecycler))
    plt.figure(1)
    plt.title(title)
    plt.legend(legend, loc='upper left')
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()


def make_table(contents):
    pass


def save_data(alg, num_vcs, traffic, allocator, dat):
    data_filename = alg + '-' + str(num_vcs) + '-'  + traffic + '-'  + allocator
    with open(data_filename, 'w') as file:
        file.write(json.dumps(dat))
    with open(data_filename + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dat)


def load_data(alg, num_vcs, traffic, allocator):
    data_filename = alg + '-' + str(num_vcs) + '-'  + traffic + '-'  + allocator
    all_data = []
    with open(data_filename, 'r') as file:
        text = file.read()
        data = json.loads(text)
    return data


#Main Loop
if __name__ == '__main__':
    simulate = True
    load_previous = False
    if simulate:
        all_data = []
        for algorithm in algorithms:
            update_config('0.00', alg=algorithm)
            data = run_simulation()
            all_data.append(data)
            save_data(algorithm, data)
        plot_data(all_data)
    if load_previous:
        all_data = load_data()
        plot_data(all_data)
        make_table(all_data)
