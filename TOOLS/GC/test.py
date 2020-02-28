from pygarble.alice import *
#from pygarble.bob import *
#on_input_gates = [[0, "AND", [0, 1]], [1, "XOR", [2, 3]], [2, "OR", [0,3]]]
#mid_gates = [[3, "XOR", [0, 1]], [4, "OR", [1, 2]]]
#output_gates = [[5, "OR", [3, 4]]]

#single add-gate
#on_input_gates = [[0, "XOR", [0, 2]], [1, "XOR", [1, 2]], [2, "AND", [2, 2]], [3, "AND", [0, 0]]]
#mid_gates = [[4, "AND", [0, 1]]]
#output_gates = [[5, "XOR", [1, 3]], [6, "XOR", [2, 4]]]

#double add-gate
on_input_gates = [[0, "XOR", [0, 2]], [1, "XOR", [1, 2]], [2, "AND", [2, 2]], [3, "AND", [0, 0]], [7, "AND", [3, 3]], [8, "AND", [4, 4]]]
mid_gates = [[4, "AND", [0, 1]], [6, "XOR", [2, 4]], [9, "XOR", [6, 7]], [10, "XOR", [6, 8]], [11, "AND", [9, 10]]]
output_gates = [[5, "XOR", [1, 3]], [12, "XOR", [7, 10]], [13, "XOR", [6, 11]]]

mycirc = Circuit(5, on_input_gates, mid_gates, output_gates)
my_input = [x[y] for x, y in zip(mycirc.poss_inputs, [0, 0, 0, 0, 0])]
print(mycirc.fire(my_input))