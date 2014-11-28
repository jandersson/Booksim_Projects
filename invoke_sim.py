__author__ = 'jonas'

from subprocess import call

#Global State
config_filename = "sim_config"


#Helper Functions
def invoke():
    """
    This function invokes the simulator.
    :return:
    """
    call(["booksim", config_filename])

#Main Loop
if __name__ == '__main__':
    invoke()