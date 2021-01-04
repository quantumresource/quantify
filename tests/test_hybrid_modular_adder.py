import cirq
from mathematics.shor1611 import *
import numpy as np


def test_hybrid_modular_adder():
    
    simulator = cirq.Simulator()
    
    # n+1 (size of b) must be a power of two because the Incrementer operates on 2 registers of equal size
    # These registers result from the splitting of the register b during the recursion steps 
    # All the resulting registers must be even hence why #b must be a power of two
    
    n = 7
    
    b = [cirq.NamedQubit("b"+str(i)) for i in range(n+1)]
    
    # One garbage qubit
    g = cirq.NamedQubit("grbg_qubit")
    
    # control qubit
    control = cirq.NamedQubit("ctrl")
    
    # Size of the ring/Field
    for N in range(2,2**n-1): 
        for a in range(N):
            for value_of_b in range(N):
                print(f"{a} + {value_of_b} % {N} = {(a + value_of_b) % N}")
                circuit = HybridModularAdder(hardwired_constant =a, sum_register=b, garbage_qubit=g, control=control, N=N).construct_circuit()

                qubits = sorted(list(circuit.all_qubits()))[::-1]
                intial_state = [0] * 2 ** (len(qubits))
                intial_state[value_of_b] = 1
                intial_state = np.array(intial_state, dtype=np.complex64)
                result = simulator.simulate(circuit, qubit_order=qubits, initial_state=intial_state)
                # print(result)
                assert(np.where(result.final_state == 1)[0][0] == (a+value_of_b)%N)
                