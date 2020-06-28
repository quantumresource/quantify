import cirq
import numpy as np

from mathematics.shor1611 import ShorRecursiveAdder


def example1():
    # The register to which the constant is to be added
    a = [cirq.NamedQubit("A" + str(i)) for i in range(4)]

    # The qubit holding the carry gate result
    c = cirq.NamedQubit("c")

    constant = 8
    circuit = ShorRecursiveAdder(a, constant, c).construct_circuit()[::-1]
    print(circuit)
    # print(circuit1)
    simulator = cirq.Simulator()
    qubits = sorted(list(circuit.all_qubits()))[::-1]
    intial_state = [0] * 2 ** (len(qubits))
    intial_state[2] = 1
    intial_state = np.array(intial_state, dtype=np.complex64)
    result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
    print(result)


def example2():
    # The register to which the constant is to be added
    a = [cirq.NamedQubit("A" + str(i)) for i in range(8)]

    # The qubit holding the carry gate result
    c = cirq.NamedQubit("c")
    constant = 4

    # Qubit controlling the operation
    control = [cirq.NamedQubit("c1"), cirq.NamedQubit("c2")]
    circuit = ShorRecursiveAdder(A_reg=a, hardwired_constant=constant, garbage=c, control=control) \
        .construct_controlled_circuit(True)
    print(circuit)

    # Circuit simulation
    simulator = cirq.Simulator()
    qubits = sorted(list(circuit.all_qubits()))[::-1]
    intial_state = [0] * 2 ** (len(qubits))
    intial_state[512+1024+1] = 1
    intial_state = np.array(intial_state, dtype=np.complex64)
    result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
    print(result)


def main():
    example1()
    example2()


if __name__ == "__main__":
    main()
