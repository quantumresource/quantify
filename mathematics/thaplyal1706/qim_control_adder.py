"""
    Implementation of control adder from : arXiv 1706.05113v1
"""
import cirq

from utils.counting_utils import count_ops


class QimControlAdder:
    def __init__(self, A, B, ctrl, ancillae=None, type=True):
        """

        :param A: The quantum register holding the first integer
        :param B: The quantum register second the first integer (the last N qubits of the addition result will be
                 registered in B)
        :param ctrl: The qubit controlling the operation
        :param ancillae: The two needed ancillae
        :param type: Boolean parameter : if True the result will be in N+1 precision otherwise, otherwise it will
                 be in N qubit precision
        """
        self.A = A
        self.B = B
        self.ctrl = ctrl
        self.size = len(A)
        self.type = type
        if ancillae != None:
            self.ancillae = ancillae
        else:
            self.ancillae = [cirq.NamedQubit("ancilla1"), cirq.NamedQubit("ancilla2")]

    def construct_circuit(self):
        self.circuit = cirq.Circuit()
        # The first set of CNOTs
        firs_set_of_CNOTs = [cirq.Moment([cirq.CNOT(self.A[i], self.B[i]) for i in range(1, self.size)])]
        # The set of CNOTs between the Ais
        second_set_of_CNOTs = []
        # The set of Toffolis between Ai Bi and Ai+1
        firs_set_of_toff = [cirq.Moment([cirq.TOFFOLI(self.B[0], self.A[0], self.A[1])])]
        # The set of Toffolis in the second part of the circuit
        second_set_of_toff = [cirq.TOFFOLI(self.ctrl, self.A[0], self.B[0])]
        single = []
        for i in range(1, self.size - 1):
            # Constructing the first part of the circuit
            second_set_of_CNOTs.append(cirq.Moment([cirq.CNOT(self.A[i], self.A[i + 1])]))
            firs_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.B[i], self.A[i], self.A[i + 1])]))

            # Constructing the last part of the circuit
            second_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[i], self.B[i])]))

        # Appending the last Toffoli of the first set
        second_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[-1], self.B[-1])]))

        # Adding or removing the N+1st qubit depending on the choice
        if self.type:
            firs_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.B[-1], self.A[-1], self.ancillae[1])]))  # here
            second_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.ancillae[1], self.ancillae[0])]))  # here
            single = [cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[-1], self.ancillae[0])])]

        # Constructing the circuit
        self.circuit.append(firs_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        self.circuit.append(single, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)  # here
        self.circuit.append(second_set_of_CNOTs[::-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        self.circuit.append(firs_set_of_toff, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        firs_set_of_toff = firs_set_of_toff[::-1]
        second_set_of_toff = second_set_of_toff[::-1]
        for i in range(len(firs_set_of_toff)):
            self.circuit.append(second_set_of_toff[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
            self.circuit.append(firs_set_of_toff[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        self.circuit.append(second_set_of_toff[-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        self.circuit.append(second_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        self.circuit.append(firs_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        return self.circuit

    def verify_toffoli(self):
        formula = 3*len(self.A) + 2
        number_of_toffolis = count_ops(self.circuit, [cirq.TOFFOLI])
        verif = (formula == number_of_toffolis)
        return verif

