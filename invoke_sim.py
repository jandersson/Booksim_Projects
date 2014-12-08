__author__ = 'Jonas Andersson'

from subprocess import PIPE, Popen
import re
import json
import fileinput
import matplotlib.pyplot as plt
import csv

#Global State
config_filename = "sim_config"
inject_rate = re.compile(r"(?P<identifier>injection_rate)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)(?P<semicolon>;)")
avg_packet_latency = re.compile(r"(?P<identifier>Packet latency average)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)")
algorithm_re = re.compile(r"(?P<identifier>routing_function)(?P<assign_op>[ =]+)(?P<algorithm>[a-z_]+)(?P<semicolon>;)")
num_vcs_re = re.compile(r"(?P<identifier>num_vcs)(?P<assign_op>[ =]+)(?P<value>[0-9]+)(?P<semicolon>;)")
allocator_re = re.compile(r"(?P<identifier>)")

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


def update_config(new_rate, alg=None, vc_num=None, alloc=None):
    if alloc:
        print('Allocation set to ' + alloc)
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(allocator_re.sub('vc_allocator = ' + alloc + ';', line), end='')
    if vc_num:
        print('Setting number of virtual channels to: ' + vc_num)
        with fileinput.input(config_filename, inplace=True) as config:
            for line in config:
                print(num_vcs_re.sub('num_vcs = ' + vc_num + ';', line), end='')

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
    title = 'Average Latency vs. Offered Load'
    for data_set in results:
        x_vals = [x[0] for x in data_set]
        y_vals = [y[1] for y in data_set]
        plt.plot(x_vals, y_vals)
    plt.figure(1)
    plt.title(title)
    plt.legend(algorithms)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()


def make_table(contents):
    pass


def save_data(alg, dat):
    with open(alg, 'w') as file:
        file.write(json.dumps(dat))
    with open(alg + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dat)


def load_data():
    all_data = []
    for alg in algorithms:
        with open(alg, 'r') as file:
            text = file.read()
            data = json.loads(text)
            all_data.append(data)
    return all_data


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
