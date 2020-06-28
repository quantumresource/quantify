import cirq
import numpy as np

from mathematics.shor1611 import ShorCarryGate


def example1():
    # Quantum register
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    # Dirty ancillae
    b = [cirq.NamedQubit("b" + str(i)) for i in range(3)]

    # Qubit for carry result
    c = cirq.NamedQubit("c")

    # classical value
    constant = 11
    uncontrolled_carry_circuit = ShorCarryGate(a, constant, b, c).construct_circuit()

    print(uncontrolled_carry_circuit)

    simulator = cirq.Simulator()
    qubits = sorted(list(uncontrolled_carry_circuit.all_qubits()))[::-1]
    initial_state = [0] * 2 ** (len(qubits))
    initial_state[128] = 1
    initial_state = np.array(initial_state, dtype=np.complex64)
    result = simulator.simulate(uncontrolled_carry_circuit, qubit_order=qubits,
                                initial_state=initial_state)
    print(result)


def example2():
    # Quantum register
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    # Dirty ancillae
    b = [cirq.NamedQubit("b" + str(i)) for i in range(3)]

    # Qubit for carry result
    c = cirq.NamedQubit("c")

    # Qubit controlling control of the operation
    control = cirq.NamedQubit("control")

    # classical value
    constant = 1
    controlled_carry_circuit = ShorCarryGate(a, constant, b, c, control)\
        .construct_controlled_circuit(False)

    print(controlled_carry_circuit)

    simulator = cirq.Simulator()
    qubits = sorted(list(controlled_carry_circuit.all_qubits()))[::-1]
    initial_state = [0] * 2 ** (len(qubits))
    initial_state[15] = 1
    initial_state = np.array(initial_state, dtype=np.complex64)
    result = simulator.simulate(controlled_carry_circuit, qubit_order=qubits,
                                initial_state=initial_state)
    print(result)


def main():
    example1()
    example2()


if __name__ == "__main__":
    main()
