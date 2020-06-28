import cirq
import numpy as np

from mathematics.thaplyal1706 import QimControlAdder


def example():
    a = [cirq.NamedQubit("a" + str(i)) for i in range(2)]
    b = [cirq.NamedQubit("b" + str(i)) for i in range(2)]
    control = cirq.NamedQubit("control")
    circuit = QimControlAdder(a, b, control, type=True).construct_circuit()
    print(circuit)
    simulator = cirq.Simulator()
    qubits = sorted(list(circuit.all_qubits()))[::-1]
    intial_state = [0] * 2 ** (len(qubits))
    # Setting control to '1' a to '3' and b to '1' the result should 4 = '100', a stays
    # unchaged as well as control note that ancilla1 is the most significant of the sum
    intial_state[83] = 1
    intial_state = np.array(intial_state, dtype=np.complex64)
    result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)


    print(result)


def __main__():
    example()


if __name__ == "__main__":
    __main__()
