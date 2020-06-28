import cirq
from mathematics.shor1611.shor_recursive_adder import ShorRecursiveAdder
import numpy as np

"""
    Test for the recursive adder 
"""
def test_recursive_adder():
    # n is the bit-size integer
    n = 8

    # A is the quantum register holding the integer
    A = [cirq.NamedQubit("A" + str(i)) for i in range(n)]

    # g is the qubit which holds the result of the carry operation (refer to figure 5 from 1611)
    g = cirq.NamedQubit("g")

    # Test the recursive adder on multiple constants
    for constant in [0,2,5,7]:
        circuit = ShorRecursiveAdder(A, constant, g).construct_circuit()
        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        intial_state = [0]*2**(len(qubits))

        # Note that the addition ignores the last bit of the result as defined in the paper.
        # Hence we test on the list of integers that when added to c doesn't result in overflow (last bit = 1),
        # because this bit is a parameter and always set back to its original value.
        # Long story short we only get the n bits of the addition
        list_of_possible_integers = [i for i in range(2**n-constant)]

        # Test the recursive adder on all possible list of integers (without overflow)
        for i in list_of_possible_integers:
            intial_state[i]=1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
            assert result.final_state[i+constant] == 1
            intial_state[i] = 0


"""
    Test the controlled recursive adder 
"""

def test_controlled_recursive_adder():
    # Bit size of integer
    n = 8

    # Register holding the integer
    A = [cirq.NamedQubit("A" + str(i)) for i in range(n)]

    # Qubit for holding the result of the carry opration
    g = cirq.NamedQubit("g")

    # To control weather the addition happens or not. In this test we set its value to one
    # to allow the addition
    control = [cirq.NamedQubit("control")]

    # Setting the value of the control to one
    index_shift = 2**n

    # Testing the adder on multiple classical constant
    for constant in [0, 2, 5, 7]:
        circuit = ShorRecursiveAdder(A, constant, g, control).construct_controlled_circuit(True)
        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        intial_state = [0] * 2 ** (len(qubits))

        # Same setting in the previous test : the last bit of the result is ignored
        list_of_possible_integers = [i for i in range(index_shift, index_shift+2 ** n - constant)]
        for i in list_of_possible_integers:
            intial_state[i] = 1
            intial_state = np.array(intial_state, dtype=np.complex64)
            result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
            # print(constant, i)
            assert result.final_state[i + constant] == 1
            intial_state[i] = 0