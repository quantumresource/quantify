import cirq

"""
    Implementation of Carry gate from arXiv:1611.07995v2
"""


class CarryUsingDirtyAncilla:
    def __init__(self, a, c, g, ancilla):
        """
        :param c: classical constant
        :param a: quantum register
        :param g: dirty ancillae
        :param ancilla: the ancilla wich will carry the result
        """
        self.a, self.c, self.g, self.ancilla = a, c, g, ancilla

    def construct_circuit(self):
        n = len(self.a)
        b = bin(self.c)[2:].zfill(n)[::-1]
        circuit = cirq.Circuit()
        moment1 = [cirq.CNOT(self.g[-1], self.ancilla)]
        moments, moment3 = [cirq.TOFFOLI(self.a[0], self.a[1], self.g[0])], []
        if b[1] == '1':
            moments += [cirq.X(self.a[1]), cirq.CNOT(self.a[1], self.g[0])]
        for i in range(2, n):
            moments += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            moment3 += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            if b[i] == '1':
                moments += [cirq.X(self.a[i]), cirq.CNOT(self.a[i], self.g[i - 1])]
        circuit.append(moment1)
        circuit.append(moments[::-1])
        circuit.append(moment3)
        circuit.append(moment1)
        return circuit