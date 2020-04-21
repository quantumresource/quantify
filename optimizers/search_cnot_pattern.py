import cirq


class SearchCNOTPattern():

    def optimize_circuit(self, circuit : cirq.Circuit):
        number_patterns = 0

        for mi, moment in enumerate(circuit):
            for op in moment:
                if op.gate == cirq.ops.CNOT:
                    control = op.qubits[0]
                    target = op.qubits[1]

                    m2 = circuit.next_moment_operating_on([target], mi + 1)
                    if m2 is None:
                        continue

                    m2_op = circuit.operation_at(target, m2)

                    if m2_op.gate == cirq.ops.CNOT:
                        m2_control = m2_op.qubits[0]
                        m2_target = m2_op.qubits[1]

                        if m2_control != target:
                            continue

                        m3 = circuit.next_moment_operating_on([m2_target], m2 + 1)
                        if m3 is None:
                            continue

                        m3_op = circuit.operation_at(m2_target, m3)
                        if m3_op.gate == cirq.ops.CNOT:
                            m3_control = m3_op.qubits[0]
                            m3_target = m3_op.qubits[1]

                            if m3_control != control:
                                continue
                            if m3_target != m2_target:
                                continue

                            print("found a pattern", mi, op, m2_op, m3_op)
                            number_patterns += 1