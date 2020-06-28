import cirq
import numpy as np

from mathematics.shor1611.shor_incrementer import ShorIncrementer

def main():
    # Register to be incremented
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    # Dirty ancillae
    g = [cirq.NamedQubit("g" + str(i)) for i in range(4)]

    # Qubit controlling the operation
    r = cirq.NamedQubit("r")

    circuit = ShorIncrementer(a, g, r).construct_circuit()
    print(circuit)

    # Result simulation
    simulator = cirq.Simulator()
    qubits = sorted(list(circuit.all_qubits()))[::-1]
    initial_state = [0] * 2 ** (len(qubits))
    initial_state[256] = 1
    initial_state = np.array(initial_state, dtype=np.complex64)
    result = simulator.simulate(circuit, qubit_order=qubits, initial_state=initial_state)
    print(result)


if __name__ == "__main__":
    main()