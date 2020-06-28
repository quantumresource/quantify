"""
    Implement Shor's algorithm from figure 2 arXiv 1611.07995
"""

import cmath

import cirq
import numpy as np

from mathematics.shor1611 import ShorModularMultiplier


class ShorAlgorithm:
    def __init__(self, harwired_constant, exponentiation_result, ancillae, control, N, zero_qubit):
        """
        :param harwired_constant: hard wired constant
        :param exponentiation_result: 
        :param ancillae:
        :param control:
        :param N:
        :param zero_qubit:
        """
        self.hardwired_constant, self.exponentiation_result, self.ancillae, self.control, self.N, self.zero_qubit = harwired_constant, exponentiation_result, ancillae, control, N, zero_qubit

    def construct_circuit(self):
        # As described we need 2n controlled multiplication operations
        size = 2 * len(self.exponentiation_result)

        # First multiplication
        moments = [cirq.H(self.control[0])]

        moments += ShorModularMultiplier(hardwired_constant=self.hardwired_constant ** (2 ** 0),
                                         product_register=self.ancillae, x=self.exponentiation_result,
                                         N=self.N, zero_qubit=self.zero_qubit).construct_circuit(
            self.control).moments

        moments += [cirq.H(self.control[0])]

        moments += [cirq.measure(self.control[0])]

        circuit = cirq.Circuit(moments)

        # Set of measurements
        measurements = []

        simulator = cirq.Simulator()
        qubits = self.exponentiation_result + self.ancillae + [self.zero_qubit] + self.control
        initial_state = np.array([0] * 2 ** len(qubits))
        # Initializing the input with | 1 >
        initial_state[1] = 1

        result = simulator.simulate(circuit, initial_state=initial_state, qubit_order=qubits)

        # print(result.measurements[self.control[0].name])

        # Append the value of the first measurement
        measurements.append(result.measurements[self.control[0].name])

        # 2n-1 remaining multiplication
        for i in range(1, size):
            # Adding a NOT gate depending on the value of the last measurement
            if measurements[-1] == 1:
                moments += [cirq.X(self.control[0])]

            moments += [cirq.H(self.control[0])]

            moments += ShorModularMultiplier(hardwired_constant=self.hardwired_constant ** (2 ** i),
                                             product_register=self.ancillae, x=self.exponentiation_result,
                                             N=self.N, zero_qubit=self.zero_qubit).construct_circuit(
                self.control).moments

            # Preparing theta the angle of rotation gate
            theta = -cmath.pi * sum(2 ** (j - i) * measurements[j] for j in range(len(measurements)))

            # Matrix of rotation gate
            R_theta = cirq.MatrixGate(np.array([[1, 0], [0, cmath.exp(1j * theta)]]))

            moments += [R_theta.on(self.control[0])]

            moments += [cirq.H(self.control[0])]

            moments += [cirq.measure(self.control[0])]

            circuit.append(moments)
            result = simulator.simulate(circuit, initial_state=initial_state, qubit_order=qubits)
            measurements.append(result.measurements[self.control[0].name])

        return circuit, measurements, result

