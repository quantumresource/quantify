"""
    Implementing a controlled modular adder
"""

import cirq
import numpy as np

from mathematics.shor1611 import ShorRecursiveAdder
from mathematics.shor1611.shor_incrementer import ShorIncrementer
from mathematics.thaplyal1706.control_adder import ControlAdder


class ControlledModularAdder:
    def __init__(self, a, b, N, control):
        """
        :param a: First integer
        :param b: Second integer
        :param N: N = 0 modN
        :param control: control qubit
        """
        self.a, self.b, self.N, self.control = a, b, N, control

    def construct_circuit(self):
        moments = []
        circuit = ControlAdder(self.a, self.b, self.control) \
            .construct_circuit()
        moments += ControlAdder(self.b, self.N)
        circuit.append(moments)
        return circuit


a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]
b = [cirq.NamedQubit("b" + str(i)) for i in range(4)]
N = [cirq.NamedQubit("N" + str(i)) for i in range(5)]
control = cirq.NamedQubit("control")
circuit = ControlledModularAdder(a, b, N, control).construct_circuit()
print(circuit)
simulator = cirq.Simulator()
qubits = sorted(list(circuit.all_qubits()))[::-1]
initial_state = [0]*2**len(qubits)
initial_state = np.array(initial_state)
initial_state[1026] = 1
result = simulator.simulate(circuit, qubit_order=qubits, initial_state=initial_state)
print(circuit.all_qubits())
#
# a = cirq.NamedQubit("a")
# circuit = cirq.Circuit(cirq.X(a), cirq.measure(a))
# simulator = cirq.Simulator()
# result = simulator.run(circuit, repetitions=1)
# if result.measurements['a'] == np.array([[1]]):
#     circuit.append(cirq.Moment([cirq.H(a)]))
# print("Results:")
# print(result.measurements['a'])
# print(circuit)