"""
Implementation of the carry ripple adder in the form presented by Gidney
in https://arxiv.org/pdf/1709.06648.pdf
"""

import cirq

from .recycled_gate import RecycledGate

class CarryRipple4TAdder():

    def __init__(self, nr_qubits = 3, use_dual_ancilla = False):
        print("Carry Ripple Adder")
        self._qubit_order = []
        self.circuit = None

        self.use_dual_ancilla = use_dual_ancilla

        self.qubits_a = [cirq.NamedQubit("a" + str(i)) for i in range(nr_qubits)]
        self.qubits_b = [cirq.NamedQubit("b" + str(i)) for i in range(nr_qubits)]
        self.qubits_t = [cirq.NamedQubit("t" + str(i)) for i in range(nr_qubits)]
        self.qubits_d = [cirq.NamedQubit("d" + str(i)) for i in range(nr_qubits)]

        for i in range(nr_qubits):
            self._qubit_order.append(self.qubits_a[i])
            self._qubit_order.append(self.qubits_b[i])
            if i != nr_qubits - 1:
                self._qubit_order.append(self.qubits_t[i])
            if self.use_dual_ancilla:
                if i != nr_qubits - 1:
                    self._qubit_order.append(self.qubits_d[i])

        self.construct_circuit(nr_qubits)

    @property
    def qubit_order(self):
        return self._qubit_order

    def start_remote_CNOT(self, dual_qubit, current_control):
        # Assume the ancilla is initialised in +
        self.circuit.append(RecycledGate("||X |+>").on(dual_qubit),
                            strategy=cirq.InsertStrategy.NEW)

        self.circuit.append(cirq.ops.CNOT.on(dual_qubit,
                                             current_control),
                            strategy = cirq.InsertStrategy.NEW)


    def close_remote_CNOT(self, dual_qubit, current_control):
        # Insert measurement and reinitialisation in zero
        self.circuit.append(RecycledGate("||Z |0>").on(current_control),
                            strategy=cirq.InsertStrategy.NEW)

        # Move the state back to the original control
        self.circuit.append(cirq.ops.CNOT.on(dual_qubit,
                                             current_control),
                            strategy=cirq.InsertStrategy.NEW)

        # Assume the ancilla is initialised in +
        self.circuit.append(RecycledGate("||X |+>").on(dual_qubit),
                            strategy=cirq.InsertStrategy.NEW)


    def construct_circuit(self, nr_qubits):
        self.circuit = cirq.Circuit()

        """
            Propagate the carry ripple
        """

        if self.use_dual_ancilla:
            for ripple_i in range(nr_qubits - 1):
                carry_in_idx = ripple_i - 1
                if ripple_i != 0:
                    self.start_remote_CNOT(self.qubits_d[carry_in_idx],
                                           self.qubits_t[carry_in_idx])


        for ripple_i in range(nr_qubits - 1):
            carry_in_idx = ripple_i - 1

            # This is the control qubit for the three CNOTs
            # from the addition subcircuit
            cnot_control_qubit = self.qubits_t[carry_in_idx]

            if self.use_dual_ancilla:
                if ripple_i != 0:
                    cnot_control_qubit = self.qubits_d[carry_in_idx]

            # The two CNOTs
            if ripple_i != 0:
                self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                            self.qubits_a[ripple_i]),
                               strategy = cirq.InsertStrategy.NEW)
                self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                            self.qubits_b[ripple_i]),
                               strategy=cirq.InsertStrategy.NEW)


            # The Toffoli gate
            self.circuit.append(cirq.ops.TOFFOLI.on(self.qubits_a[ripple_i],
                                               self.qubits_b[ripple_i],
                                               self.qubits_t[ripple_i]),
                           strategy=cirq.InsertStrategy.NEW)

            if ripple_i != 0:
                self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                            self.qubits_t[ripple_i]),
                               strategy=cirq.InsertStrategy.NEW)


        if self.use_dual_ancilla:
            for ripple_i in range(nr_qubits - 1):
                carry_in_idx = ripple_i - 1
                if ripple_i != 0:
                    self.close_remote_CNOT(self.qubits_d[carry_in_idx],
                                           self.qubits_t[carry_in_idx])


        """
            The CNOT in the middle
        """
        cnot_control_qubit = self.qubits_t[nr_qubits - 2]
        # if self.use_dual_ancilla:
        #     self.start_remote_CNOT(self.qubits_d[nr_qubits - 2], cnot_control_qubit)
        #     cnot_control_qubit = self.qubits_d[nr_qubits - 2]

        self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                         self.qubits_b[nr_qubits - 1]))

        # if self.use_dual_ancilla:
        #     self.close_remote_CNOT(self.qubits_d[nr_qubits - 2],
        #                            self.qubits_t[nr_qubits - 2])


        """
            Propagate back the carry ripple
        """

        # if self.use_dual_ancilla:
        #     for ripple_i in range(nr_qubits - 1):
        #         carry_in_idx = ripple_i - 1
        #         if ripple_i != 0:
        #             self.start_remote_CNOT(self.qubits_d[carry_in_idx],
        #                                    self.qubits_t[carry_in_idx])

        # the reverse range of indices in Python's own words
        for ripple_i in range(nr_qubits - 2, -1, -1):
            carry_in_idx = ripple_i - 1

            # This is the control qubit for the three CNOTs
            # from the addition subcircuit
            cnot_control_qubit = self.qubits_t[carry_in_idx]

            if self.use_dual_ancilla:
                if ripple_i != 0:
                    cnot_control_qubit = self.qubits_d[carry_in_idx]
                    self.start_remote_CNOT(self.qubits_d[carry_in_idx],
                                           self.qubits_t[carry_in_idx])

            if ripple_i != 0:
                self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                                self.qubits_t[ripple_i]),
                               strategy=cirq.InsertStrategy.NEW)

            # The Toffoli gate
            self.circuit.append(cirq.ops.TOFFOLI.on(self.qubits_a[ripple_i],
                                               self.qubits_b[ripple_i],
                                               self.qubits_t[ripple_i]),
                           strategy=cirq.InsertStrategy.NEW)

            # Only one CNOT this time
            if self.use_dual_ancilla:
                if ripple_i != 0:
                    self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                                self.qubits_a[ripple_i]),
                                   strategy=cirq.InsertStrategy.NEW)
                    self.close_remote_CNOT(self.qubits_d[carry_in_idx],
                                           self.qubits_t[carry_in_idx])
            else:
                if ripple_i != 0:
                    self.circuit.append(cirq.CNOT.on(cnot_control_qubit,
                                                self.qubits_a[ripple_i]),
                                   strategy=cirq.InsertStrategy.NEW)


        """
            Compute the sums
        """
        for sum_i in range(nr_qubits):
            strat = cirq.InsertStrategy.INLINE
            if sum_i == 0:
                strat = cirq.InsertStrategy.NEW
            self.circuit.append(cirq.ops.CNOT.on(self.qubits_a[sum_i],
                                            self.qubits_b[sum_i]),
                           strategy=strat)

    def __str__(self):
        return self.circuit.to_text_diagram(use_unicode_characters=False,
                                          qubit_order = self.qubit_order)