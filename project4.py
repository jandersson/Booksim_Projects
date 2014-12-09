#Use the BookSim simulator to study the effect of virtual channels and virtual
#channel allocators on the average latency vs. offered load for a torus network
#with k=16 and n=2 under dimension-order routing
#
#The virtual channel buffer size is 8
#
#The number of virtual channels is either 8 or 16
#
#The traffic pattern is either random or nearest neighbor
#
#The virtual channel and switch allocators are either wavefront or separable
#input first.
#
#Provide the plots (plus the actual values for the plots) for the eight resulting
#cases and a discussion of your observations

__author__ = 'Jonas Andersson'

import invoke_sim

#Global State
algorithm = "dim_order"
num_vcs = [8, 16]
traffic = ['uniform', 'neighbor']
allocators = ['wavefront', 'separable_input_first']

#Main Loop
if __name__ == "__main__":
    simulate = False
    load_previous = True
    all_data = []
    if simulate:
        for vcs in num_vcs:
            for pattern in traffic:
                for method in allocators:
                    invoke_sim.update_config('0.00', alloc=method, vc_num=vcs, traffic=pattern)
                    data = invoke_sim.run_simulation()
                    all_data.append(data)
                    invoke_sim.save_data(algorithm, vcs, pattern, method, data)
        invoke_sim.plot_data(all_data)
    elif load_previous:
        legend = []
        print("Loading previous simulation")
        for vcs in num_vcs:
            for pattern in traffic:
                for method in allocators:
                    data = invoke_sim.load_data(alg=algorithm, num_vcs=vcs, traffic=pattern, allocator=method)
                    all_data.append(data)
                    legend.append(algorithm + '-' + str(vcs) + '-'  + pattern + '-'  + method)
        invoke_sim.plot_data(all_data, legend)
