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

#Global State

num_vcs = [8, 16]
traffic = ['uniform', 'neighbor']
allocators = ['wavefront', 'separable_input_first']
