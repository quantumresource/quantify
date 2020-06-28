import cirq
import numpy as np

from mathematics.shor1611 import ShorModularAdder

def example1():
    # 1000 -> 0111 -> 1000 = 8
    # 8

    # Nr of bits + sign
    nr_bits = 4

    # Register holding the integer
    b = [cirq.NamedQubit(f'b{i}') for i in range(nr_bits)]

    # Dirty ancillae register
    g = [cirq.NamedQubit(f'g{i}') for i in range(nr_bits)]

    # Qubit initialized to 0 and holds the result of carry operation
    carry = cirq.NamedQubit('xcarry')

    # Constant value
    a = 4

    # x
    value_of_b = 7

    # The integer N
    N = 8

    """
    4+0 = 4
    4+1 = 5
    4+2 = 6
    4+3 = 7
    4+4 = 0
    4+5 = 1
    4+6 = 2
    4+7 = 3
    """
    for dec_b in range(0, 8, 1):
        print(f"B:{dec_b} + A:{a} %N:{N} =? {(a+dec_b)%N}")
        # Constructing the circuit
        circuit = ShorModularAdder(value_of_b, a, N,
                                   b, g, carry).construct_circuit()
        # Printing circuit
        # print(circuit)

        # Simulation
        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        initial_state = np.array([0]*2**(len(qubits)))
        # |0 0000 BBBB>
        initial_state[dec_b] = 1
        result = simulator.simulate(circuit, qubit_order=qubits, initial_state=initial_state)
        print(result)

def example2():
    # Register holding the integer
    b = [cirq.NamedQubit('b' + str(i)) for i in range(4)]

    # Dirty ancillae register
    g = [cirq.NamedQubit('g' + str(i)) for i in range(4)]

    # Qubit initialized to 0 and holds the result of carry operation
    carry = cirq.NamedQubit('x')

    # Constant value
    a = 4

    # x
    value_of_b = 7

    # The integer N
    N = 8

    # Constructing the circuit
    circuit, result = ShorModularAdder(value_of_b, a, N, b, g, carry) \
        .construct_circuit_with_sign_gate()
    # Printing circuit
    print(circuit)
    # printing result
    print(result)


def __main__():
    example1()
    # example2()


if __name__ == "__main__":
    __main__()