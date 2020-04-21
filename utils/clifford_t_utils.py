import cirq


def is_t_or_s_gate(cirq_op):
    # simplistic verification of T or S gate. These are not Hermitian.
    # based on the fact that the circuit generators use cirq.T,S
    # whenever a T,S gate is required
    return isinstance(cirq_op, cirq.GateOperation) and \
        cirq_op.gate in [cirq.T, cirq.T**-1, cirq.S, cirq.S**-1]


def reverse_moments(list_of_moments):
    n_moments = []
    for moment in reversed(list_of_moments):
        n_moment = cirq.Moment()
        for op in moment:
            if is_t_or_s_gate(op):
                n_moment = n_moment.with_operation(op**-1)
            else:
                # everything else is Clifford
                # and I assume CNOT, H
                n_moment = n_moment.with_operation(op)

        n_moments.append(n_moment)
    return n_moments


def is_controlled_parallel_x(operation):
    return (
                   isinstance(operation, cirq.ops.ControlledOperation)
                   and
                   isinstance(operation.sub_operation, cirq.ops.ParallelGateOperation)
                   and (operation.sub_operation.gate == cirq.ops.X)
    )\
           or operation.gate == cirq.ops.CNOT


def has_control_qubit(operation, qubit):
    if operation.gate == cirq.ops.CNOT:
        return operation.qubits[0] == qubit
    elif is_controlled_parallel_x(operation):
        return qubit in operation.controls