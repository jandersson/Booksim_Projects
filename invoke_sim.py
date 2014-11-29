__author__ = 'Jonas Andersson'

from subprocess import call
import re
import fileinput

#Global State
config_filename = "sim_config"
inject_rate = re.compile(r"(?P<identifier>injection_rate)(?P<assign_op>[ =]+)(?P<value>[.0-9]+)(?P<semicolon>;)")
rates = [round(rate * 0.01, 3) for rate in range(100)]


#Helper Functions
def invoke():
    """
    This function invokes the simulator.
    :return:
    """
    call(["booksim", config_filename])


def update_config(new_rate):
    with fileinput.input(config_filename, inplace=True) as config:
        for line in config:
            print(inject_rate.sub('injection_rate = ' + str(new_rate) + ';', line), end='')

#Main Loop
if __name__ == '__main__':
    update_config("0.15")
    invoke()