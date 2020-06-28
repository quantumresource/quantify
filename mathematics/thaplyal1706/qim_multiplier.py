"""
    Implementation of the multiplier from https://arxiv.org/abs/1706.06752
"""

import cirq
from mathematics.thaplyal1706 import QimControlAdder
from mathematics.thaplyal1706 import QimControlToffoli

class QimMultiplier:
    def __init__(self, A, B):
        """

        :param A: First operand
        :param B: Second operand
        """
        self.A = A
        self.B = B
        self.size = len(A)
        # The qubits holding the product
        self.P = [cirq.NamedQubit('P'+str(i)) for i in range(2*self.size+1)]

    def multiply(self):
        circuit = cirq.Circuit()
        circuit.append(QimControlToffoli(self.B[0], self.A, self.P[0:self.size]).construct_moments())
        for i in range(1, self.size):
            # Add and shift
            circuit += QimControlAdder(self.A, self.P[i:i + self.size], self.B[i], ancillae=[self.P[i + self.size], self.P[i + 1 + self.size]]).construct_circuit()
        return circuit
