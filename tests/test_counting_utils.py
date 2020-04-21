import cirq

import utils.counting_utils as cu

def test_count_op_depth_1():
    qubit = cirq.NamedQubit("qubit")

    circuit = cirq.Circuit()

    circuit.append(cirq.ops.X.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.X.on(qubit))

    # The circuit should have depth 2 for X
    assert(cu.count_op_depth(circuit, [cirq.ops.X]) == 2)

def test_count_ops():
    qubit = cirq.NamedQubit("qubit")

    circuit = cirq.Circuit()

    circuit.append(cirq.ops.X.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.X.on(qubit))

    # The circuit should have 3 X and Y gates in total
    assert(cu.count_ops(circuit, [cirq.ops.X, cirq.ops.Y]) == 3)