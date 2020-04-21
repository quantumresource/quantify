import cirq
import cirq.optimizers

import optimizers as cnc

def test_optimise_hadamards():

    circ = cirq.Circuit()
    qubit_a = cirq.NamedQubit("a")

    circ.append(cirq.ops.H.on(qubit_a))
    circ.append(cirq.ops.H.on(qubit_a))
    circ.append(cirq.ops.H.on(qubit_a))

    # print("1", circ)

    cncl = cnc.CancelNghHadamards()
    cncl.optimize_circuit(circ)

    # print("2", circ)

    dropempty = cirq.optimizers.DropEmptyMoments()
    dropempty.optimize_circuit(circ)

    # print("3", circ)

    assert(len(circ) == 1)