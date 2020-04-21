import cirq
from mathematics.control_adder  import ControlAdder
from mathematics.control_toffoli import ControlToffoli

class multiplier:
    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.size = len(A)
        self.P = [cirq.NamedQubit('P'+str(i)) for i in range(2*self.size+1)]

    def multiply(self):
        circuit = cirq.Circuit()
        circuit.append(ControlToffoli(self.B[0], self.A, self.P[0:self.size]).construct_moments())
        for i in range(1, self.size):
            circuit += ControlAdder(self.A, self.P[i:i+self.size], self.B[i], ancillae=[self.P[i+self.size], self.P[i+1+self.size]]).construct_circuit()
        return circuit
