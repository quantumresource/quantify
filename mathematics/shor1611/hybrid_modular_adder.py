"""
    The procedure is taken from arXiv:9511018 but the used adder is taken from
    arXiv : 1611.07995
"""

import cirq

from mathematics.shor1611 import ShorRecursiveAdder


class HybridModularAdder:
    def __init__(self, hardwired_constant, sum_register, garbage_qubit, control, N):
        """

        :param hardwired_constant: hardwired constant
        :param sum_register: quantum register holding the result at the end
        :param garbage_qubit: qubit needed for the addition operation
        :param control: qubit holding the sign of a+b-N
        :param N: size of the ring (Field for Shor's case)
        """
        self.hardwired_constant, self.sum_register, self.garbage_qubit, self.control, self.N =  hardwired_constant, sum_register, garbage_qubit, control, N

    def construct_circuit(self):
        moments = []

        """
            Normal addition but it is not check if mod N
        """
        # Add the hardwired constant to the input in sum_register
        # a+b
        moments += ShorRecursiveAdder(self.sum_register, self.hardwired_constant, self.garbage_qubit)\
            .construct_circuit().moments

        """
            Part two - make it mod N
        """
        # Subtract N from the sum
        # a+b - N
        moments += ShorRecursiveAdder(self.sum_register, self.N, self.garbage_qubit)\
            .construct_circuit().moments[::-1]
        # Copy the sign qubit of the a+b-N to the control qubit
        moments += [cirq.CNOT(self.sum_register[-1], self.control)]
        # Depending on the value of the control qubit either add N back
        # or leave it as it is
        # a+b
        moments += ShorRecursiveAdder(self.sum_register, self.N, self.garbage_qubit, control=[self.control])\
            .construct_controlled_circuit(True)

        """
            Part three - reset the self.control qubit requires again two adders
        """
        # Resetting the control qubit to |0>
        # First we subtract the hardwired constant from the modular sum
        # a+b - a
        moments += ShorRecursiveAdder(self.sum_register, self.hardwired_constant, self.garbage_qubit) \
                       .construct_circuit().moments[::-1]

        # Then we reset the value of the control qubit depending on the sign qubit
        # of the previous operatio in
        moments += [cirq.X(self.sum_register[-1])]
        moments += [cirq.CNOT(self.sum_register[-1], self.control)]
        moments += [cirq.X(self.sum_register[-1])]

        # Add the constant back
        # a + b - a + a = a + b
        moments += ShorRecursiveAdder(self.sum_register,
                                      self.hardwired_constant,
                                      self.garbage_qubit).construct_circuit().moments


        circuit = cirq.Circuit(moments)
        return circuit


    def construct_controlled_circuit(self, control_qubit):
        moments = []
        # Add the hardwired constant to the input in sum_register
        moments += ShorRecursiveAdder(self.sum_register, self.hardwired_constant,
                                      self.garbage_qubit, control=control_qubit)\
            .construct_controlled_circuit(True).moments
        # Subtract N from the sum
        moments += ShorRecursiveAdder(self.sum_register, self.N,
                                      self.garbage_qubit, control=control_qubit) \
                       .construct_controlled_circuit(True).moments[::-1]
        # Copy the sign qubit of the a+b-N to the control qubit

        moments += [cirq.ControlledOperation(control_qubit + [self.sum_register[-1]], cirq.X(self.control))]
        # moments += [cirq.TOFFOLI(control_qubit, self.sum_register[-1], self.control)]
        # Depending on the value of the control qubit either add N back
        # or leave it as it is
        moments += ShorRecursiveAdder(self.sum_register, self.N, self.garbage_qubit, control=control_qubit+[self.control]) \
            .construct_controlled_circuit(True)
        # Resetting the control qubit to |0>
        # First we subtract the hardwired constant from the modular sum
        moments += ShorRecursiveAdder(self.sum_register, self.hardwired_constant,
                                      self.garbage_qubit, control=control_qubit) \
                       .construct_controlled_circuit(True).moments[::-1]
        # Then we reset the value of the control qubit depending on the sign qubit
        # of the previous operatioin
        # moments += [cirq.CNOT(control_qubit, self.sum_register[-1])]
        # moments += [cirq.TOFFOLI(control_qubit, self.sum_register[-1], self.control)]
        # moments += [cirq.CNOT(control_qubit, self.sum_register[-1])]
        moments += [cirq.ControlledOperation(control_qubit, cirq.X(self.sum_register[-1]))]
        moments += [cirq.ControlledOperation(control_qubit + [self.sum_register[-1]], cirq.X(self.control))]
        moments += [cirq.ControlledOperation(control_qubit, cirq.X(self.sum_register[-1]))]

        # Add the constant back
        moments += ShorRecursiveAdder(self.sum_register,
                                      self.hardwired_constant,
                                      self.garbage_qubit,
                                      control=control_qubit).construct_controlled_circuit(True).moments
        circuit = cirq.Circuit(moments)
        return circuit
