__author__ = 'Jonas Andersson'

from subprocess import PIPE, Popen
import re
import fileinput
import matplotlib.pyplot as plt

#Global State
config_filename = "sim_config"
inject_rate = re.compile(r"(?P<identifier>injection_rate)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)(?P<semicolon>;)")
avg_packet_latency = re.compile(r"(?P<identifier>Packet latency average)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)")
rates = [round(rate * 0.01, 3) for rate in range(0, 100, 5)]


#Helper Functions
def invoke():
    """
    This function invokes the simulator and dumps the output to a file
    :return:
    """
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


def update_config(new_rate):
    with fileinput.input(config_filename, inplace=True) as config:
        for line in config:
            print(inject_rate.sub('injection_rate = ' + str(new_rate) + ';', line), end='')


def run_simulation():
    data = []
    for rate in rates:
        update_config(str(rate))
        invoke()
        data_point = (rate, get_value())
        data.append(data_point)
    return data

#Main Loop
if __name__ == '__main__':
    data = run_simulation()
    x_vals = [x[0] for x in data]
    y_vals = [y[1] for y in data]
    plt.plot(x_vals, y_vals)
    plt.show()