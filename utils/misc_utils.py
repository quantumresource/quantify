import cirq

def my_bin(value, nr_bits):
    # Get the integer bits of the controls/search by padding to n bits
    return bin(value)[2:].zfill(nr_bits)


def is_prev_and_next_cnot_controls(circuit, qubit, index1, index2):

    p_idx = circuit.prev_moment_operating_on([qubit], index1)
    n_idx = circuit.next_moment_operating_on([qubit], index2 + 1)

    if p_idx is None or n_idx is None:
        return False

    p_op = circuit.operation_at(qubit, p_idx)
    n_op = circuit.operation_at(qubit, n_idx)

    if p_op.gate == cirq.CNOT and \
        n_op.gate == cirq.CNOT and \
        p_op.qubits[0] == qubit and \
        n_op.qubits[0] == qubit:
            # Mark the CNOTs
            setattr(p_op, "allow", True)
            setattr(n_op, "allow", True)
            return True

    return False


def transfer_flags(circuit, qubit, index1, index2):

    p_idx = circuit.prev_moment_operating_on([qubit], index1)
    n_idx = circuit.next_moment_operating_on([qubit], index2 + 1)

    if p_idx is None or n_idx is None:
        return False

    p_op = circuit.operation_at(qubit, p_idx)
    n_op = circuit.operation_at(qubit, n_idx)

    setattr(p_op, "allow", True)
    setattr(n_op, "allow", True)


def remove_all_flags(circuit):
    for moment in circuit:
        for op in moment:
            if hasattr(op, "allow"):
                delattr(op, "allow")

def flag_operations(circuit, gate_types):
    for moment in circuit:
        for op in moment:
            if op.gate in gate_types:
                setattr(op, "allow", True)

def has_flag(operation):
    return hasattr(operation, "allow")