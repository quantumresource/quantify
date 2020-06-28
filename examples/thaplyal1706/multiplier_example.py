import cirq
import numpy as np

from mathematics.thaplyal1706 import QimMultiplier


def example():
    # First integer
    a = [cirq.NamedQubit('A' + str(i)) for i in range(4)]

    # Second integer
    b = [cirq.NamedQubit('B' + str(i)) for i in range(4)]

    # Constructing circuit
    circuit = QimMultiplier(a, b).multiply()

    print(circuit)

    # Running the circuit
    simulator = cirq.Simulator()
    qubits = sorted(list(circuit.all_qubits()))[::-1]
    intial_state = [0] * 2 ** (len(qubits))
    # Setting A to '2' and b to '2' the result should be 4
    intial_state[34] = 1
    intial_state = np.array(intial_state, dtype=np.complex64)
    result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
    print(result)


def __main__():
    example()


if __name__ == "__main__":
    example()
