"""
    Implementation of control adder from : arXiv:0910.2530, 2009
"""
import cirq


class TakahashiAdder:
    def __init__(self, A, B, ancillae=None, type = True):
        self.A = A
        self.B = B
        self.size = len(A)
        self.type = type
        if ancillae != None:
            self.ancillae = ancillae
        else:
            self.ancillae = [cirq.NamedQubit("ancilla1") ,cirq.NamedQubit("ancilla2")]

    def construct_circuit(self):
        circuit = cirq.Circuit()
        # The set of CNOTs between Ai and Bi
        firs_set_of_CNOTs=[cirq.Moment([cirq.CNOT(self.A[i], self.B[i]) for i in range(1, self.size)])]

        # The set of CNOTs between Ai and Ai+1
        second_set_of_CNOTs=[]

        # The set of CNOTs between Ai, Bi and Ai+1
        firs_set_of_toff=[cirq.Moment([cirq.TOFFOLI(self.B[0], self.A[0], self.A[1])])]

        last_set_of_toff=[cirq.Moment([cirq.CNOT(self.A[0], self.B[0])])]

        single=[]
        for i in range(1, self.size-1):
            # Constructing the first part of the circuit
            second_set_of_CNOTs.append(cirq.Moment([cirq.CNOT(self.A[i], self.A[i+1])]))
            firs_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.B[i], self.A[i], self.A[i+1])]))

            # Constructing the last part of the circuit
            last_set_of_toff.append(cirq.Moment([cirq.CNOT(self.A[i], self.B[i])]))
        last_set_of_toff.append(cirq.Moment([cirq.CNOT(self.A[-1], self.B[-1])]))

        # Adding or removing the N+1st qubit depending on choice
        if self.type:
            firs_set_of_toff.append(cirq.Moment([cirq.TOFFOLI(self.B[-1], self.A[-1], self.ancillae[0])])) # here
            single = [cirq.Moment([cirq.CNOT(self.A[-1], self.ancillae[0])])]

        # Constrcting the fist half of the circuit
        circuit.append(firs_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(single, strategy=cirq.InsertStrategy.NEW_THEN_INLINE) # here
        circuit.append(second_set_of_CNOTs[::-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(firs_set_of_toff, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        # Balancing the circuit
        if self.type:
            firs_set_of_toff = firs_set_of_toff[::-1][1:]
        else:
            firs_set_of_toff = firs_set_of_toff[::-1]

        # Constructing the last part of the circuit
        last_set_of_toff = last_set_of_toff[::-1]
        for i in range(len(firs_set_of_toff)):
            circuit.append(last_set_of_toff[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
            circuit.append(firs_set_of_toff[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(last_set_of_toff[-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(second_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(firs_set_of_CNOTs, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        return circuit