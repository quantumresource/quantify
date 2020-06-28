"""
    Implementation of Incrementer using Thaplyal and Takahashi's adders from
    arXiv:1706.0511v1 and arXiv:0910.2530, 2009
"""
from mathematics.thaplyal1706 import QimControlAdder
from mathematics.takahashi0910 import TakahashiAdder

import cirq

class ShorIncrementer:
    def __init__(self, A, B, ctrl=None, ancilla=None):
        """
        :param A: the register to be incremented
        :param B: dirty ancilla register
        :param ctrl: control qubit
        """

        self.A = A
        self.B = B
        self.ctrl = ctrl
        if ancilla != None:
            self.B += [ancilla]
    """
        Controlled incrementer 
    """
    def construct_circuit(self):
        circuit = cirq.Circuit()
        moments = []

        # Particular case
        if len(self.A) == 1:
            moments += [cirq.CNOT(self.ctrl, self.A[0])]
            circuit.append(moments)
        else:
            # General case
            # Subtracting the content of the dirty B register from A (A-B)
            step1 = QimControlAdder(self.B, self.A, self.ctrl, type=False)\
                .construct_circuit().moments[::-1]

            # Preparing not(B)-1
            step2 = [cirq.X(i) for i in self.B]

            # Subtracting not(B)-1 from A+1 resulting in A
            step3 = QimControlAdder(self.B, self.A, self.ctrl, type=False)\
                .construct_circuit().moments[::-1]

            # Restoring B to its original value
            step4 = [cirq.X(i) for i in self.B]

            # constructing the corresponding circuit
            circuit.append(step1)
            circuit.append(step2)
            circuit.append(step3)
            circuit.append(step4)
        return circuit

    """
        General incrementer without any control qubit
    """
    def construct_unctrolled_circuit(self):
        circuit = cirq.Circuit()
        moments = []

        # Particular case
        if len(self.A) == 1:
            moments += [cirq.X(self.A[0])]
            circuit.append(moments)
        else:
            # General case
            # Using Takahashi's adder instead of the controlled adder of Thaplyal
            # The idea remains the same
            step1 = TakahashiAdder(self.B, self.A, type=False) \
                        .construct_circuit().moments[::-1]

            step2 = [cirq.X(i) for i in self.B]

            step3 = TakahashiAdder(self.B, self.A, type=False) \
                        .construct_circuit().moments[::-1]

            step4 = [cirq.X(i) for i in self.B]

            # Constructing the circuit
            circuit.append(step1)
            circuit.append(step2)
            circuit.append(step3)
            circuit.append(step4)
        return circuit
