"""
Implementation of the carry ripple adder in the form presented by Cuccaro
in https://arxiv.org/pdf/quant-ph/0410184.pdf
"""

import cirq

from .recycled_gate import RecycledGate

class CarryRipple8TAdder():

    def __init__(self, nr_qubits = 3, use_dual_ancilla = False):
        print("Carry Ripple Adder")
        self._qubit_order = []
        self.circuit = None

        self.use_dual_ancilla = use_dual_ancilla

        self.qubit_c = cirq.NamedQubit("c")
        self.qubit_z = cirq.NamedQubit("z")

        self.qubits_a = [cirq.NamedQubit("a" + str(i)) for i in range(nr_qubits)]
        self.qubits_b = [cirq.NamedQubit("b" + str(i)) for i in range(nr_qubits)]
        self.qubits_d = [cirq.NamedQubit("d" + str(i)) for i in range(nr_qubits)]

        self._qubit_order.append(self.qubit_c)
        for i in range(nr_qubits):
            self._qubit_order.append(self.qubits_b[i])
            self._qubit_order.append(self.qubits_a[i])

            if self.use_dual_ancilla:
                if i != nr_qubits - 1:
                    self._qubit_order.append(self.qubits_d[i])
        self._qubit_order.append(self.qubit_z)

        self.construct_circuit(nr_qubits)

    @property
    def qubit_order(self):
        return self._qubit_order

    def __str__(self):
        return self.circuit.to_text_diagram(use_unicode_characters=False,
                                          qubit_order = self.qubit_order)


    def MAJ_gate(self, qubit_1, qubit_2, qubit_3):

        self.circuit.append(cirq.ops.CNOT.on(qubit_3, qubit_1),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_3, qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.TOFFOLI.on(qubit_1, qubit_2, qubit_3),
                            strategy = cirq.InsertStrategy.NEW)

    def UMA_2cnot_gate(self, qubit_1, qubit_2, qubit_3):

        self.circuit.append(cirq.ops.TOFFOLI.on(qubit_1, qubit_2, qubit_3),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_3, qubit_1),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_1, qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

    def UMA_3cnot_gate(self, qubit_1, qubit_2, qubit_3):

        self.circuit.append(cirq.ops.X.on(qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_1, qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.TOFFOLI.on(qubit_1, qubit_2, qubit_3),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.X.on(qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_3, qubit_2),
                            strategy = cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(qubit_3, qubit_1),
                            strategy = cirq.InsertStrategy.NEW)





    def construct_circuit(self, nr_qubits):
        self.circuit = cirq.Circuit()

        """
            Propagate the carry ripple
        """

        for i in range(nr_qubits):
            qubit_1 = self.qubit_c
            if i > 0:
                qubit_1 = self.qubits_a[i-1]
            qubit_2 = self.qubits_b[i]
            qubit_3 = self.qubits_a[i]

            self.MAJ_gate(qubit_1, qubit_2, qubit_3)

        self.circuit.append(cirq.ops.CNOT(self.qubits_a[nr_qubits - 1],
                                          self.qubit_z))

        for i in range(nr_qubits - 1, -1, -1):
            qubit_1 = self.qubit_c
            if i > 0:
                qubit_1 = self.qubits_a[i-1]
            qubit_2 = self.qubits_b[i]
            qubit_3 = self.qubits_a[i]

            self.UMA_3cnot_gate(qubit_1, qubit_2, qubit_3)
