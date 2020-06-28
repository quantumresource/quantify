import cirq
import numpy as np

from mathematics.shor1611 import HybridModularAdder


def example1():
    simulator = cirq.Simulator()

    # The register to which the constant is to be added
    b = [cirq.NamedQubit("b"+str(i)) for i in range(4)]
    # One garbage qubit
    g = cirq.NamedQubit("grbg_qubit")
    # control qubit
    control = cirq.NamedQubit("ctrl")
    # Size of the ring/Field
    N = 7
    for a in range(N):
        for value_of_b in range(N):
            print(f"{a} + {value_of_b} % {N} = {(a + value_of_b) % N}")
            circuit = HybridModularAdder(hardwired_constant =a, sum_register=b, garbage_qubit=g, control=control, N=N).construct_circuit()

            qubits = sorted(list(circuit.all_qubits()))[::-1]
            intial_state = [0] * 2 ** (len(qubits))
            intial_state[value_of_b] = 1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)

            print(result)


def example2():
    simulator = cirq.Simulator()
    # The register to which the constant is to be added
    b = [cirq.NamedQubit("b"+str(i)) for i in range(4)]
    # One garbage qubit
    g = cirq.NamedQubit("grbg_qubit")
    # control qubit
    control = cirq.NamedQubit("ctrl")
    control_qubit = [cirq.NamedQubit("xctrl")]
    # Size of the ring/Field
    N = 7
    for a in range(N):
        for value_of_b in range(N):
            print(f"{a} + {value_of_b} % {N} = {(a + value_of_b) % N}")
            circuit = HybridModularAdder(hardwired_constant =a, sum_register=b, garbage_qubit=g, control=control, N=N)\
                .construct_controlled_circuit(control_qubit)

            qubits = sorted(list(circuit.all_qubits()))[::-1]
            intial_state = [0] * 2 ** (len(qubits))
            control_activation = 2**(len(qubits)-1)
            intial_state[control_activation+value_of_b] = 1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
            # |0>|product%N>|a>
            print(result)

def __main__():
    example1()
    example2()


if __name__ == "__main__":
    __main__()