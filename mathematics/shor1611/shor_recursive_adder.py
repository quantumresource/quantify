"""
    Implementation of Recursive adder from Fig. 5 in arXiv:1611.07995v2
"""

import cirq
import math

from mathematics.shor1611.shor_incrementer import ShorIncrementer
from mathematics.shor1611.shor_carry_gate import ShorCarryGate


class ShorRecursiveAdder:
    def __init__(self, A_reg, hardwired_constant, garbage, control=None):
        """
        :param A_reg: the quantum register where the addition result is stored
        :param hardwired_constant: the classical integer
        :param garbage: qubit used for garbage/ancilla
        :param control: is used to control the application of the recursive adder
        """
        self.A = A_reg
        self.C = hardwired_constant

        self.garbage = garbage
        self.control = control

        # Binary rep of the constant c
        self.bin_C = bin(self.C)[2:].zfill(len(self.A))[::-1]

    """
        Controlled version of construct circuit 
    """

    def construct_controlled_circuit(self, choice = True):
        """
        :param choice: The value on which to condition: True = |1>, False = |0>
        :return:
        """
        moments = []
        for i in range(int(math.log2(len(self.A)))):
            number_of_blocks = 2 ** i
            step = len(self.A) // number_of_blocks
            n = math.ceil(len(self.A) / (2 * number_of_blocks))
            for j in range(2 ** i):
                l = int(self.bin_C[j * step:(2 * j + 1) * n][::-1], 2)
                # First comes the incrementer from figure 5
                moments += ShorIncrementer(self.A[(2 * j + 1) * n:(2 * j + 1) * n + n],
                                           self.A[j * step:(2 * j + 1) * n],
                                           ctrl=self.garbage).construct_circuit().moments


                # Then the set of CNOTs from figure 5
                moments += [cirq.CNOT(self.garbage, k) for k in self.A[(2 * j + 1) * n:(2 * j + 1) * n + n]]

                # Afterwards the Carry operation from figure 5 to see if wen need to increment Xh
                moments += ShorCarryGate(a=self.A[j * step:(2 * j + 1) * n], c=l,
                                         g=self.A[(2 * j + 1) * n:(2 * j + 1) * n + n - 1],
                                         ancilla=self.garbage, control=self.control) \
                    .construct_controlled_circuit(choice).moments

                # Then the incrementer controlled by the result of the Carry operation
                moments += ShorIncrementer(self.A[(2 * j + 1) * n:(2 * j + 1) * n + n],
                                           self.A[j * step:(2 * j + 1) * n],
                                           self.garbage).construct_circuit().moments

                # Reset the carry_result qubit to its original value
                moments += ShorCarryGate(a=self.A[j * step:(2 * j + 1) * n], c=l,
                                         g=self.A[(2 * j + 1) * n:(2 * j + 1) * n + n - 1], ancilla=self.garbage,
                                         control=self.control).construct_controlled_circuit(choice).moments

                # lastly the CNOTs
                moments += [cirq.CNOT(self.garbage, k) for k in self.A[(2 * j + 1) * n:(2 * j + 1) * n + n]]

        circuit = cirq.Circuit()

        # Last layer is the 1-bit addition
        for i in range(len(self.bin_C)):
            if self.bin_C[i] == '1':
                if choice:
                    # moments += [cirq.CNOT(self.control, self.A[i])]
                    moments += [cirq.ControlledOperation(self.control, cirq.X(self.A[i]))]
                else:
                    moments += [cirq.ControlledOperation(self.control, cirq.X(self.A[i]), control_values=[0]*len(self.control))]
        circuit.append(moments)
        return circuit

    """
        The following function is the unctrolled version of the recursive adder
    """
    def construct_circuit(self):
        moments = []
        for i in range(int(math.log2(len(self.A)))):
            number_of_blocks = 2 ** i
            step = len(self.A) // number_of_blocks
            n = math.ceil(len(self.A) / (2 * number_of_blocks))
            for j in range(2 ** i):
                # Extract the corresponding bits
                l = int(self.bin_C[j * step:(2 * j + 1) * n][::-1], 2)

                # First incrementer from figure 5
                moments += ShorIncrementer(self.A[(2 * j + 1) * n:(2 * j + 1) * n + n],
                                           self.A[j * step:(2 * j + 1) * n],
                                           self.garbage).construct_circuit().moments

                # Then set of CNOTs from figure 5
                moments += [cirq.CNOT(self.garbage, k) for k in self.A[(2 * j + 1) * n:(2 * j + 1) * n + n]]

                # The carry operation from figure 5
                moments += ShorCarryGate(a=self.A[j * step:(2 * j + 1) * n], c=l,
                                         g=self.A[(2 * j + 1) * n:(2 * j + 1) * n + n - 1],
                                         ancilla=self.garbage).construct_circuit().moments

                # Then the incrementer controlled by the carry_result qubit
                moments += ShorIncrementer(self.A[(2 * j + 1) * n:(2 * j + 1) * n + n],
                                           self.A[j * step:(2 * j + 1) * n],
                                           self.garbage).construct_circuit().moments

                # Resetting the carry qubit to its original value
                moments += ShorCarryGate(self.A[j * step:(2 * j + 1) * n], l,
                                         self.A[(2 * j + 1) * n:(2 * j + 1) * n + n - 1],
                                         self.garbage).construct_circuit().moments

                # Lastly the CNOTs
                moments += [cirq.CNOT(self.garbage, k) for k in self.A[(2 * j + 1) * n:(2 * j + 1) * n + n]]

        circuit = cirq.Circuit()

        # Last layer 1-bit addition
        for i in range(len(self.bin_C)):
            if self.bin_C[i] == '1':
                moments += [cirq.X(self.A[i])]
        circuit.append(moments)
        return circuit