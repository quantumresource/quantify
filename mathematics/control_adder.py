"""
Implementation of control adder from :
"""

import cirq

class ControlAdder:
    def __init__(self, A, B, ctrl, ancillae=None):
        self.A = A
        self.B = B
        self.ctrl = ctrl
        self.size = len(A)
        if ancillae != None:
            self.ancillae = ancillae
        else:
            self.ancillae = [cirq.NamedQubit("ancilla1") ,cirq.NamedQubit("ancilla2")]


    def construct_circuit(self):
        circuit = cirq.Circuit()
        m1=[cirq.Moment([cirq.CNOT(self.A[i], self.B[i]) for i in range(1, self.size)])]
        m2=[]
        m3=[cirq.Moment([cirq.TOFFOLI(self.B[0], self.A[0], self.A[1])])]
        m4=[cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[0], self.B[0]),
                         cirq.CNOT(self.A[1], self.A[2])])]
        single=[cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[-1], self.ancillae[0])])]
        for i in range(1, self.size-1):
            m2.append(cirq.Moment([cirq.CNOT(self.A[i], self.A[i+1])]))
            m3.append(cirq.Moment([cirq.TOFFOLI(self.B[i], self.A[i], self.A[i+1])]))
            m4.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[i], self.B[i])]))
        m3.append(cirq.Moment([cirq.TOFFOLI(self.B[-1], self.A[-1], self.ancillae[1])]))
        m4.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.A[-1], self.B[-1])]))
        m4.append(cirq.Moment([cirq.TOFFOLI(self.ctrl, self.ancillae[1], self.ancillae[0])]))

        circuit.append(m1, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(single, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(m2[::-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(m3, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        m3 = m3[::-1]
        m4 = m4[::-1]
        for i in range(len(m3)):
            circuit.append(m4[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
            circuit.append(m3[i], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(m4[-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(m2[1:], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(m1, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        return circuit
        # print(circuit)




