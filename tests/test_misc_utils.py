import cirq
import utils.misc_utils as mu

def test_transfer_flag():
    qubit = cirq.NamedQubit("qubit")
    circuit = cirq.Circuit()
    circuit.append(cirq.ops.X.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.X.on(qubit))

    mu.flag_operations(circuit, [cirq.ops.Y])

    mu.transfer_flags(circuit, qubit, 1, 2)

    for op in circuit.all_operations():
        if op.gate == cirq.ops.X:
            assert (mu.has_flag(op) == True)

def test_has_flag():
    obj1 = cirq.ops.X
    assert(mu.has_flag(obj1) == False)

    setattr(obj1, "allow", True)
    assert (mu.has_flag(obj1) == True)

def test_flag_operations():
    qubit = cirq.NamedQubit("qubit")
    circuit = cirq.Circuit()
    circuit.append(cirq.ops.X.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.X.on(qubit))

    mu.flag_operations(circuit, [cirq.ops.X])

    for op in circuit.all_operations():
        if op.gate == cirq.ops.X:
            assert (mu.has_flag(op) == True)
        else:
            assert (mu.has_flag(op) == False)

def test_remove_all_flags():
    qubit = cirq.NamedQubit("qubit")
    circuit = cirq.Circuit()
    circuit.append(cirq.ops.X.on(qubit))
    circuit.append(cirq.ops.Y.on(qubit))
    circuit.append(cirq.ops.X.on(qubit))

    mu.flag_operations(circuit, [cirq.ops.X])
    mu.remove_all_flags(circuit)

    for op in circuit.all_operations():
        assert (mu.has_flag(op) == False)