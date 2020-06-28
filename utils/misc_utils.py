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


def print_matrix(matrix, precision):
    """
     https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
    :param matrix:
    :return:
    
    """

    format_string = "%." + str(precision) + "f"

    float_formatter = lambda x: format_string % x

    s = [[str(float_formatter(e)) for e in row] for row in matrix]
    # s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    # fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    s = '\n'.join(table)
    return s


def get_latex_representation(self):
    # get the latex code of the circuit
    # important to include "\usepackage{qcircuit}" in your latex file
    # to avoid compilation errors
    return cirq.contrib.circuit_to_latex_using_qcircuit(self.construct_circuit_with_sign_gate)
