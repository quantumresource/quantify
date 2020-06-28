import cirq
import mathematics.thaplyal1706.qim_multiplier as mt
import numpy as np


def test_multiplier():
    # n represents the
    n = 3

    # A and B are the numbers to be multiplied
    A = [cirq.NamedQubit('a' + str(i)) for i in range(n)]
    B = [cirq.NamedQubit('b' + str(i)) for i in range(n)]

    # instanciate the multiplier class and invoke the multiply method
    # the result is the corresponding circuit
    circuit = mt.QimMultiplier(A, B).multiply()
    # print(circuit)

    simulator = cirq.Simulator()

    # sort the qubits in a way such that B has the most significant bits then A then P
    qubits = sorted(list(circuit.all_qubits()))[::-1]

    intial_state = [0] * 2 ** (len(qubits))

    """Now consider B and A as a concatinated bitstring with B having the most significant bits
        Afterwards add 2n+1 bits of 0 which represents P0, P1...P2n
    """

    """the list of all possible integers is exactly the range(2^(2n)) but we need to shift it 
        in order to initialize the qubits of P to 0
    """
    shift = 2 ** n - 1
    list_of_possible_integers = [i << shift for i in range(2 ** (2 * n))]
    print(list_of_possible_integers)
    for i in list_of_possible_integers:
        intial_state[i] = 1
        # state[1920]=1
        intial_state = np.array(intial_state, dtype=np.complex64)
        result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
        BA = i >> shift
        B_times_A = BA % (2 ** 3) * (BA >> n)
        assert (np.where(result.final_state == 1)[0][0] == i + B_times_A)
        intial_state[i] = 0
