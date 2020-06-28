import cirq
import numpy as np

from mathematics.shor1611 import ShorModularMultiplier


def example1():
    # The register to which the constant is to be added
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    b = [cirq.NamedQubit("b" + str(i)) for i in range(4)]

    # One garbage qubit
    zero = cirq.NamedQubit("zero_qubit")
    control = [cirq.NamedQubit("zx")]
    # Size of the ring/Field
    N = 7
    # Note that the constant shoud be comprime with N
    # Since N = 7 is prime => gcd(x, N) = 1 for x<N
    for constant in range(N):
        for value_of_b in range(N):
            print(f"{constant} x {value_of_b} % {N} = {(constant * value_of_b) % N}")
            circuit = ShorModularMultiplier(N=N, hardwired_constant=constant,
                                            product_register=b, x=a, zero_qubit=zero).\
                construct_circuit(control=control)
            simulator = cirq.Simulator()
            qubits = sorted(list(circuit.all_qubits()))[::-1]
            intial_state = [0] * 2 ** (len(qubits))
            intial_state[512+value_of_b] = 1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
            print(result)


def example2():
    # The register to which the constant is to be added
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    b = [cirq.NamedQubit("b" + str(i)) for i in range(4)]

    # One garbage qubit
    zero = cirq.NamedQubit("zero_qubit")
    # Size of the ring/Field
    N = 7
    # Note that the constant shoud be comprime with N
    # Since N = 7 is prime => gcd(x, N) = 1 for x<N
    for constant in range(N):
        for value_of_b in range(N):
            print(f"{constant} x {value_of_b} % {N} = {(constant * value_of_b) % N}")
            circuit = ShorModularMultiplier(N=N, hardwired_constant=constant,
                                            product_register=b, x=a, zero_qubit=zero).\
                construct_circuit()
            simulator = cirq.Simulator()
            qubits = sorted(list(circuit.all_qubits()))[::-1]
            intial_state = [0] * 2 ** (len(qubits))
            intial_state[value_of_b] = 1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
            print(result)


def __main__():
    example1()
    example2()


if __name__ == "__main__":
    __main__()